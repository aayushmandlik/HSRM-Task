from fastapi import FastAPI
from routes.user_routes import router as user_router
from routes.admin_routes import router as admin_router
from routes.emp_routes import router as emp_router
from routes.task_routes import router as task_router
from routes.attendance_routes import router as attendance_router
from routes.admin_attendance_routes import router as admin_attendance_router
app = FastAPI()

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(emp_router)
app.include_router(task_router)
app.include_router(attendance_router)
app.include_router(admin_attendance_router)