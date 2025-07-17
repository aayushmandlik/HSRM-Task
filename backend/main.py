from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.user_routes import router as user_router
from routes.admin_routes import router as admin_router
from routes.emp_routes import router as emp_router
from routes.task_routes import router as task_router
from routes.attendance_routes import router as attendance_router
from routes.admin_attendance_routes import router as admin_attendance_router
from routes.leave_routes import router as emp_leave_router
from routes.admin_leave_routes import router as admin_leave_router
from routes.payroll_routes import router as payroll_router
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Allow Angular frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)


app.include_router(user_router)
app.include_router(admin_router)
app.include_router(emp_router)
app.include_router(task_router)
app.include_router(attendance_router)
app.include_router(admin_attendance_router)
app.include_router(emp_leave_router)
app.include_router(admin_leave_router)
app.include_router(payroll_router)