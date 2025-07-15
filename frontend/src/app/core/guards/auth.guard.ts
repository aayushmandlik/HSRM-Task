import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    const user = this.authService.getCurrentUser();
    const expectedRole = route.data['role'];

    if (!user) {
      this.router.navigate(['/auth']);
      return false;
    }

    if (expectedRole && user.role !== expectedRole) {
      this.router.navigate(['/auth']);
      return false;
    }

    return true;
  }
}