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
        this.router.navigate(['/profile']);
      })
    );
  }

  adminRegister(admin: AdminRegister): Observable<any> {
    // Assuming admin registration requires a special code; adjust logic as needed
    return this.http.post(`${this.apiUrl}/users/register`, { ...admin, role: 'admin' }).pipe(
      tap(() => console.log('Admin registered'))
    );
  }

  adminLogin(admin: AdminLogin): Observable<TokenResponse> {
    const formData = new URLSearchParams();
    formData.set('username', admin.email); // Map email to username
    formData.set('password', admin.password);

    const headers = new HttpHeaders({ 'Content-Type': 'application/x-www-form-urlencoded' });

    return this.http.post<TokenResponse>(`${this.apiUrl}/users/login`, formData.toString(), { headers }).pipe(
      tap((response) => {
        if (response.role !== 'admin') {
          throw new Error('Admin access denied');
        }
        localStorage.setItem('auth_token', JSON.stringify(response));
        this.currentUserSubject.next(response);
        this.router.navigate(['/admin/dashboard']);
      })
    );
  }

  getCurrentUser(): TokenResponse | null {
    return this.currentUserSubject.value;
  }

  getToken(): string | null {
    const user = this.getCurrentUser();
    return user ? user.access_token : null; // Adjust based on your TokenResponse structure
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
}