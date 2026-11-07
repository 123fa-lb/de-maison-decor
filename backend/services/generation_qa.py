# DEMAISON_QA_GATE_V1
"""
Generic "check the paid image, retry at most once" gate used by Lifestyle and Close-up.

  * `verify(result_bytes)` returns {"passed": bool, "correction": str, "issues": ...}.
  * If it fails and retries are enabled, the SAME request is repeated once with the review's
    correction text appended, and the better of the two images is kept.
  * Any exception (network, quota, bad image) keeps the first image. The gate can never
    turn a successful generation into a failure.

Environment (all optional):
  DEMAISON_QA_GATE=0     disable the review entirely (restores single-request behaviour)
  DEMAISON_QA_RETRY=0    keep the review (headers/logs) but never spend a second paid request
"""

import os
from io import BytesIO

from PIL import Image, ImageOps


def _extract_bytes(response):
    for candidate in getattr(response, "candidates", None) or []:
        content = getattr(candidate, "content", None)
        if not content:
            continue
        for part in content.parts or []:
            inline = getattr(part, "inline_data", None)
            if inline and getattr(inline, "data", None):
                return inline.data
    return None


def _to_image(data):
    with Image.open(BytesIO(data)) as im:
        return ImageOps.exif_transpose(im).convert("RGB")


def _usage(response):
    usage = getattr(response, "usage_metadata", None)
    return (int(getattr(usage, "prompt_token_count", 0) or 0),
            int(getattr(usage, "candidates_token_count", 0) or 0))


def gate_enabled():
    return os.getenv("DEMAISON_QA_GATE", "1").strip() != "0"


def retry_enabled():
    return os.getenv("DEMAISON_QA_RETRY", "1").strip() != "0"


def run_quality_gate(label, client, types, model, config, parts, result_bytes, response, verify):
    """
    Returns (result_bytes, response, report, extra_usage) where extra_usage = (tokens_in, tokens_out)
    spent on a retry (so cost accounting stays honest).
    """
    report = {"label": label, "retried": False, "first": None, "second": None}
    extra = (0, 0)
    try:
        first = verify(_to_image(result_bytes))
        report["first"] = {k: first.get(k) for k in ("passed", "issues", "advisory", "ratio", "checked")}
        print(f"[MAISON STUDIO] {label} QA: {report['first']}", flush=True)
        if first.get("passed") or not first.get("correction") or not retry_enabled():
            report["final"] = "accepted" if first.get("passed") else "kept_failed_no_retry"
            return result_bytes, response, report, extra

        retry_parts = list(parts) + [types.Part.from_text(text=first["correction"])]
        report["retried"] = True
        retry_response = client.models.generate_content(
            model=model, contents=[types.Content(role="user", parts=retry_parts)], config=config)
        extra = _usage(retry_response)
        retry_bytes = _extract_bytes(retry_response)
        if not retry_bytes:
            report["final"] = "retry_returned_no_image"
            return result_bytes, response, report, extra
        second = verify(_to_image(retry_bytes))
        report["second"] = {k: second.get(k) for k in ("passed", "issues", "advisory", "ratio", "checked")}
        print(f"[MAISON STUDIO] {label} QA retry: {report['second']}", flush=True)
        if second.get("passed") or len(second.get("issues") or []) < len(first.get("issues") or []):
            report["final"] = "retry_used"
            # Keep the ORIGINAL response object: the caller only reads token usage from it, and the
            # retry's usage is already reported separately in `extra` (no double counting).
            return retry_bytes, response, report, extra
        report["final"] = "retry_not_better_original_kept"
        return result_bytes, response, report, extra
    except Exception as exc:
        print(f"[MAISON STUDIO] {label} QA skipped: {exc}", flush=True)
        report["final"] = "qa_error_original_kept"
        return result_bytes, response, report, extra
