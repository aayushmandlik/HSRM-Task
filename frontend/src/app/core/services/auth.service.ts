import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
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
    return this.http.post<TokenResponse>(`${this.apiUrl}/users/login`, user).pipe(
      tap((response) => {
        localStorage.setItem('auth_token', JSON.stringify(response));
        this.currentUserSubject.next(response);
        this.router.navigate(['/profile']);
      })
    );
  }

  adminRegister(admin: AdminRegister): Observable<any> {
    return this.http.post(`${this.apiUrl}/admin/register`, admin).pipe(
      tap(() => console.log('Admin registered'))
    );
  }

  adminLogin(admin: AdminLogin): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.apiUrl}/admin/login`, admin).pipe(
      tap((response) => {
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
    return user ? user.access_token : null; // Assuming TokenResponse has a 'token' field
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