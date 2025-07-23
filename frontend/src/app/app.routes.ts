// import { Routes } from '@angular/router';
// import { AuthComponent } from './auth/auth.component';
// import { UserProfileComponent } from './employee/user-profile/user-profile.component';
// import { AdminDashboardComponent } from './admin/admin-dashboard/admin-dashboard.component';
// import { AuthGuard } from './core/guards/auth.guard';

// export const routes: Routes = [
//   { path: 'auth', component: AuthComponent },
//   { 
//     path: 'profile', 
//     component: UserProfileComponent, 
//     canActivate: [AuthGuard], 
//     data: { role: 'user' } 
//   },
//   { 
//     path: 'admin/dashboard', 
//     component: AdminDashboardComponent, 
//     canActivate: [AuthGuard], 
//     data: { role: 'admin' } 
//   },
//   { path: '', redirectTo: '/auth', pathMatch: 'full' },
//   { path: '**', redirectTo: '/auth' }
// ];

import { Routes } from '@angular/router';
import { AuthComponent } from './auth/auth.component';
import { UserProfileComponent } from './employee/user-profile/user-profile.component';
import { AdminDashboardComponent } from './admin/admin-dashboard/admin-dashboard.component';
import { AuthGuard } from './core/guards/auth.guard';
import { EmployeesComponent } from './admin/employees/employees.component';
import { TaskComponent } from './admin/task/task.component';
import { LeaveComponent } from './admin/leave/leave.component';
import { AttendanceComponent } from './admin/attendance/attendance.component';
import { PayrollComponent } from './admin/payroll/payroll.component';
import { AdminDashboardContentComponent } from './admin/admin-dashboard-content/admin-dashboard-content.component';
import { EmployeeDashboardContentComponent } from './employee/employee-dashboard-content/employee-dashboard-content.component';
import { EmployeeTaskComponent } from './employee/employee-task/employee-task.component';
import { EmployeeLeaveComponent } from './employee/employee-leave/employee-leave.component';
import { EmployeeAttendanceComponent } from './employee/employee-attendance/employee-attendance.component';

export const routes: Routes = [
  { path: 'auth', component: AuthComponent },
  { 
    path: 'profile', 
    component: UserProfileComponent, 
    canActivate: [AuthGuard], 
    data: { role: 'user' } ,
    children: [
      {path: '', redirectTo: 'dashboard', pathMatch: 'full'},
      {path: 'dashboard',component: EmployeeDashboardContentComponent, data: {title: 'Employee Dashboard'}},
      {path: 'task', component: EmployeeTaskComponent, data: { title: 'Task' } },
      {path: "leave", component: EmployeeLeaveComponent, data: {title: 'Leave'}},
      {path: "attendance", component: EmployeeAttendanceComponent, data:{title: 'Attendance'}}
    ]
  },
  { 
    path: 'admin', 
    component: AdminDashboardComponent, 
    canActivate: [AuthGuard], 
    data: { role: 'admin' }, 
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: AdminDashboardContentComponent, data: { title: 'Admin Dashboard' } },
      { path: 'employees', component: EmployeesComponent, data: { title: 'Employees' } },
      { path: 'task', component: TaskComponent, data: { title: 'Task' } },
      { path: 'leave', component: LeaveComponent, data: { title: 'Leave' } },
      { path: 'attendance', component: AttendanceComponent, data: { title: 'Attendance' } },
      { path: 'payroll', component: PayrollComponent, data: { title: 'Payroll' } }
    ]
  },
  { path: '', redirectTo: '/auth', pathMatch: 'full' },
  { path: '**', redirectTo: '/auth' }
];