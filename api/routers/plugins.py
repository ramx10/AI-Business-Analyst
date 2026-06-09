import sys
import os
import inspect
import importlib
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from utils.plugin_manager import get_plugin_manager, PLUGIN_DIR
from utils.plugin_base import BasePlugin
from api.session_store import load_df, session_exists

router = APIRouter()


@router.get("/plugins")
async def list_plugins():
    pm = get_plugin_manager()
    return JSONResponse({"plugins": pm.get_plugins()})


@router.post("/plugins/{name}/run")
async def run_plugin(name: str, data: dict):
    session_id = data.get("session_id")
    if not session_id or not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")
    df = load_df(session_id)
    params = data.get("params", {})
    pm = get_plugin_manager()
    result = pm.run_plugin(name, df, **params)
    if not result.get("success"):
        return JSONResponse(result, status_code=400)
    return JSONResponse(result)


@router.post("/plugins/install")
async def install_plugin(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are accepted.")
    dest_path = os.path.join(PLUGIN_DIR, file.filename)
    with open(dest_path, "wb") as f:
        content = await file.read()
        f.write(content)
    pm = get_plugin_manager()
    pm.reload()
    return JSONResponse({"success": True, "message": f"Plugin '{file.filename}' installed."})


@router.delete("/plugins/{name}")
async def uninstall_plugin(name: str):
    pm = get_plugin_manager()
    plugin = pm.get_plugin(name)
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin '{name}' not found.")
    for fname in os.listdir(PLUGIN_DIR):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        mod_name = fname[:-3]
        try:
            mod = importlib.import_module(mod_name)
            for _, obj in inspect.getmembers(mod):
                if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    instance = obj()
                    if instance.name == name:
                        os.remove(os.path.join(PLUGIN_DIR, fname))
                        pm.reload()
                        return JSONResponse({"success": True, "message": f"Plugin '{name}' uninstalled."})
        except Exception:
            continue
    raise HTTPException(status_code=500, detail="Could not locate plugin file.")
