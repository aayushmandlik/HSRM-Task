import { Component } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators, FormGroup } from '@angular/forms';
import { AuthService } from '../core/services/auth.service';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css']
})
export class AuthComponent {
  isUser = true;
  isLogin = true;
  userRegisterForm: FormGroup;
  userLoginForm: FormGroup;
  adminRegisterForm: FormGroup;
  adminLoginForm: FormGroup;
  errorMessage: string | null = null;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.userRegisterForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });

    this.userLoginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });

    this.adminRegisterForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      code: ['', [Validators.required]]
    });

    this.adminLoginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  toggleUserType(): void {
    this.isUser = !this.isUser;
    this.errorMessage = null;
  }

  toggleFormType(): void {
    this.isLogin = !this.isLogin;
    this.errorMessage = null;
  }

  onUserRegister(): void {
    if (this.userRegisterForm.valid) {
      this.authService.userRegister(this.userRegisterForm.value).subscribe({
        next: () => this.router.navigate(['/profile']),
        error: (err) => this.errorMessage = err.error.detail || 'Registration failed'
      });
    }
  }

  onUserLogin(): void {
    if (this.userLoginForm.valid) {
      this.authService.userLogin(this.userLoginForm.value).subscribe({
        next: () => this.router.navigate(['/profile']),
        error: (err) => this.errorMessage = err.error.detail || 'Login failed'
      });
    }
  }

  onAdminRegister(): void {
    if (this.adminRegisterForm.valid) {
      this.authService.adminRegister(this.adminRegisterForm.value).subscribe({
        next: () => this.router.navigate(['/admin/dashboard']),
        error: (err) => this.errorMessage = err.error.detail || 'Registration failed'
      });
    }
  }

  onAdminLogin(): void {
    if (this.adminLoginForm.valid) {
      this.authService.adminLogin(this.adminLoginForm.value).subscribe({
        next: () => this.router.navigate(['/admin/dashboard']),
        error: (err) => this.errorMessage = err.error.detail || 'Login failed'
      });
    }
  }
}