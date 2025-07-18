import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const AuthGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const requiredRole = route.data['role'];

  if (authService.isAuthenticated()) {
    const userRole = authService.getUserRole();
    if (requiredRole && userRole !== requiredRole) {
      if (userRole === 'user') {
        return router.createUrlTree(['/profile']);
      }
      return router.createUrlTree(['/auth']);
    }
    return true;
  } else {
    return router.createUrlTree(['/auth']);
  }
};