import { Routes } from '@angular/router';
import { AuthComponent } from './auth/auth.component';
import { UserProfileComponent } from './employee/user-profile/user-profile.component';
import { AdminDashboardComponent } from './admin/admin-dashboard/admin-dashboard.component';
import { AuthGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: 'auth', component: AuthComponent },
  { 
    path: 'profile', 
    component: UserProfileComponent, 
    canActivate: [AuthGuard], 
    data: { role: 'user' } 
  },
  { 
    path: 'admin/dashboard', 
    component: AdminDashboardComponent, 
    canActivate: [AuthGuard], 
    data: { role: 'admin' } 
  },
  { path: '', redirectTo: '/auth', pathMatch: 'full' },
  { path: '**', redirectTo: '/auth' }
];