import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { Attendance } from '../interfaces/attendance.interface';
import { AuthService } from './auth.service';

interface ApiResponse {
  message: string;
}

interface LogsResponse {
  logs: Attendance[];
}

@Injectable({
  providedIn: 'root'
})
export class AttendanceService {
  private adminBaseUrl = 'http://localhost:8000/admin/attendance';
  private empBaseUrl = 'http://localhost:8000/attendance';

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    if (!token) {
      throw new Error('No token available. Please log in.');
    }
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getAttendanceLogs(date: string): Observable<Attendance[]> {
    return this.http.get<LogsResponse>(`${this.adminBaseUrl}/logs?date=${date}`, { headers: this.getHeaders() }).pipe(
      map(response => response.logs),
      catchError(error => {
        console.error('Error fetching attendance logs:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error fetching attendance logs', detail: error.error?.detail }));
      })
    );
  }

  getMyAttendanceLogs(): Observable<Attendance[]> {
    return this.http.get<LogsResponse>(`${this.empBaseUrl}/logs/me`, { headers: this.getHeaders() }).pipe(
      map(response => response.logs),
      catchError(error => {
        console.error('Error fetching my attendance logs:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error fetching my attendance logs', detail: error.error?.detail }));
      })
    );
  }

  checkIn(): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.empBaseUrl}/checkin`, {}, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error performing check-in:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error performing check-in', detail: error.error?.detail }));
      })
    );
  }

  checkOut(): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.empBaseUrl}/checkout`, {}, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error performing check-out:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error performing check-out', detail: error.error?.detail }));
      })
    );
  }

  breakIn(): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.empBaseUrl}/breakin`, {}, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error performing break-in:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error performing break-in', detail: error.error?.detail }));
      })
    );
  }

  breakOut(): Observable<ApiResponse> {
    return this.http.post<ApiResponse>(`${this.empBaseUrl}/breakout`, {}, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error performing break-out:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error performing break-out', detail: error.error?.detail }));
      })
    );
  }
}