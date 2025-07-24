// src/app/core/services/auth.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { UserRegister, UserLogin, AdminRegister, AdminLogin, TokenResponse } from '../interfaces/user.interface';
import { tap } from 'rxjs/operators';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api'; // Adjust to your backend URL
  private currentUserSubject = new BehaviorSubject<TokenResponse | null>(null);
  currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    const tokenData = localStorage.getItem('auth_token');
    if (tokenData) {
      this.currentUserSubject.next(JSON.parse(tokenData));
    }
  }

  userRegister(user: UserRegister): Observable<any> {
    return this.http.post(`${this.apiUrl}/users/register`, user).pipe(
      tap(() => console.log('User registered'))
    );
  }

  userLogin(user: UserLogin): Observable<TokenResponse> {
    const formData = new URLSearchParams();
    formData.set('username', user.email); // Map email to username
    formData.set('password', user.password);

    const headers = new HttpHeaders({ 'Content-Type': 'application/x-www-form-urlencoded' });

    return this.http.post<TokenResponse>(`${this.apiUrl}/users/login`, formData.toString(), { headers }).pipe(
      tap((response) => {
        localStorage.setItem('auth_token', JSON.stringify(response));
        this.currentUserSubject.next(response);
        this.router.navigate(['/profile/dashboard']);
      })
    );
  }

  adminRegister(admin: AdminRegister): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/register`, admin).pipe(
      tap(() => console.log('Admin registered'))
    );
  }

  adminLogin(admin: AdminLogin): Observable<TokenResponse> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });

    return this.http.post<TokenResponse>(`${this.apiUrl}/admin/login`, admin, { headers }).pipe(
      tap((response) => {
        if (response.role !== 'admin') {
          throw new Error('Admin access denied: Role is not admin');
        }
        localStorage.setItem('auth_token', JSON.stringify(response));
        this.currentUserSubject.next(response);
        this.router.navigate(['/admin/dashboard']);
      }, (err) => {
        console.error('Admin login error:', err);
        throw err;
      })
    );
  }

  getCurrentUser(): TokenResponse | null {
    return this.currentUserSubject.value;
  }

  getToken(): string | null {
    const user = this.getCurrentUser();
    return user ? user.access_token : null; 
  }

  logout(): void {
    localStorage.removeItem('auth_token');
    this.currentUserSubject.next(null);
    this.router.navigate(['/auth']);
  }

  isAuthenticated(): boolean {
    return !!this.getCurrentUser();
  }

  getUserRole(): string | null {
    const user = this.getCurrentUser();
    return user ? user.role : null;
  }

  getAdminName(): string | null {
    const admin = this.getCurrentUser();
    return admin ? admin.name : null
  }

  getUserName(): string | null {
    const user = this.getCurrentUser();
    return user ? user.name : null 
  }
}