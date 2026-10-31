"""Auto-save generated JPEGs for 30 days, even without user downloads."""
import os, sqlite3, uuid, threading, time, logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

router = APIRouter(prefix="/api/history", tags=["Generated Images"])
BASE = Path(os.getenv("MAISON_HISTORY_DIR", str(Path(__file__).resolve().parent / "data" / "generated_history")))
DB = BASE / "history.sqlite3"
RETENTION = timedelta(days=30)
_lock = threading.RLock()
log = logging.getLogger(__name__)

def _db():
    BASE.mkdir(parents=True, exist_ok=True)
    con=sqlite3.connect(str(DB),timeout=20)
    con.execute("CREATE TABLE IF NOT EXISTS images (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, sku TEXT NOT NULL, category TEXT NOT NULL, filename TEXT NOT NULL, size INTEGER NOT NULL)")
    con.execute("CREATE INDEX IF NOT EXISTS images_created_at ON images(created_at)")
    return con

def cleanup():
    cutoff=(datetime.now(timezone.utc)-RETENTION).isoformat()
    with _lock:
        with _db() as con:
            old=con.execute("SELECT filename FROM images WHERE created_at < ?",(cutoff,)).fetchall()
            con.execute("DELETE FROM images WHERE created_at < ?",(cutoff,))
        for (name,) in old:
            try: (BASE / name).unlink(missing_ok=True)
            except OSError: log.exception("Failed to delete expired generated image")

def _cleanup_loop():
    while True:
        try: cleanup()
        except Exception: log.exception("Image history cleanup failed")
        time.sleep(6*60*60)

def start_history_cleanup():
    threading.Thread(target=_cleanup_loop,daemon=True,name="maison-history-retention").start()

def _store(data, sku, category):
    if not data or len(data)>30*1024*1024: return
    ident=uuid.uuid4().hex
    name=ident+'.jpg'
    with _lock:
        BASE.mkdir(parents=True,exist_ok=True)
        path=BASE/name
        path.write_bytes(data)
        try:
            with _db() as con:
                con.execute("INSERT INTO images VALUES (?,?,?,?,?,?)",(ident,datetime.now(timezone.utc).isoformat(),sku[:180] or 'Unassigned',category[:60] or 'Image',name,len(data)))
        except Exception:
            path.unlink(missing_ok=True)
            raise

async def archive_generated_image(request,call_next):
    response=await call_next(request)
    if request.method!='POST' or request.url.path not in ('/api/studio/generate','/api/studio/compose-local') or response.status_code!=200 or not response.headers.get('content-type','').startswith('image/jpeg'):
        return response
    # Starlette BaseHTTPMiddleware returns a streaming response. Reconstruct it after archiving.
    chunks=[]
    async for chunk in response.body_iterator:
        chunks.append(chunk)
    body=b''.join(chunks)
    try:
        _store(body,response.headers.get('X-DeMaison-SKU','Unassigned'),response.headers.get('X-DeMaison-Category','Image'))
    except Exception:
        log.exception('Image generated successfully but history archive failed')
    headers=dict(response.headers)
    headers.pop('content-length',None)
    headers.pop('x-demaison-sku',None)
    headers.pop('x-demaison-category',None)
    return Response(content=body,status_code=response.status_code,headers=headers,media_type='image/jpeg',background=response.background)

@router.get('/images')
def list_images(limit:int=300):
    cleanup()
    limit=max(1,min(limit,500))
    with _db() as con:
        con.row_factory=sqlite3.Row
        rows=con.execute("SELECT id,created_at,sku,category,size FROM images ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
    return {'retention_days':30,'images':[dict(x) for x in rows]}

@router.get('/images/{image_id}')
def get_image(image_id:str):
    if len(image_id)!=32 or not all(c in '0123456789abcdef' for c in image_id): raise HTTPException(404,'Image not found')
    cutoff=(datetime.now(timezone.utc)-RETENTION).isoformat()
    with _db() as con:
        row=con.execute('SELECT filename,sku,category FROM images WHERE id=? AND created_at>=?',(image_id,cutoff)).fetchone()
    if not row: raise HTTPException(404,'Image expired or not found')
    file=BASE/row[0]
    if not file.is_file(): raise HTTPException(404,'Image file missing')
    return FileResponse(file,media_type='image/jpeg',filename=f'{row[1]}_{row[2]}_{image_id[:8]}.jpg',headers={'Cache-Control':'private, max-age=300'})
