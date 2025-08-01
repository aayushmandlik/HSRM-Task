import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { LeaveResponse, LeaveCreate, LeaveUpdate, LeaveUpdateStatus } from '../interfaces/leave.interface';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class LeaveService {
  private adminBaseUrl = 'http://localhost:8000/admin/leave';
  private empBaseUrl = 'http://localhost:8000/Emp_leave';

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    if (!token) {
      throw new Error('No token available. Please log in.');
    }
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getPendingLeaveRequests(): Observable<LeaveResponse[]> {
    return this.http.get<LeaveResponse[]>(`${this.adminBaseUrl}/pendingrequests`, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error fetching pending leave requests:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error fetching pending leave requests', detail: error.error?.detail }));
      })
    );
  }

  getApprovedRejectedLeaveRequests(): Observable<LeaveResponse[]> {
    return this.http.get<LeaveResponse[]>(`${this.adminBaseUrl}/leaverequests`, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error fetching approved/rejected leave requests:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error fetching approved/rejected leave requests', detail: error.error?.detail }));
      })
    );
  }

  updateLeaveStatus(leaveId: string, updateData: LeaveUpdateStatus): Observable<LeaveResponse> {
    return this.http.put<LeaveResponse>(`${this.adminBaseUrl}/${leaveId}/status`, updateData, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error updating leave status:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error updating leave status', detail: error.error?.detail }));
      })
    );
  }

  getMyLeaveRequests(): Observable<LeaveResponse[]> {
    return this.http.get<LeaveResponse[]>(`${this.empBaseUrl}/my-requests`, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error fetching my leave requests:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error fetching my leave requests', detail: error.error?.detail }));
      })
    );
  }

  createLeaveRequest(leaveData: LeaveCreate): Observable<LeaveResponse> {
    return this.http.post<LeaveResponse>(`${this.empBaseUrl}/request`, leaveData, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error submitting leave request:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error submitting leaves request', detail: error.error?.detail }));
      })
    );
  }

  updateLeaveRequest(leaveId: string, updateData: LeaveUpdate): Observable<LeaveResponse> {
    return this.http.patch<LeaveResponse>(`${this.empBaseUrl}/${leaveId}`, updateData, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error updating leave:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error updating leave', detail: error.error?.detail }));
      })
    );
  }

  deleteLeaveRequest(leaveId: string): Observable<LeaveResponse> {
    return this.http.delete<LeaveResponse>(`${this.empBaseUrl}/${leaveId}`, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error deleting leave:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error deleting leave', detail: error.error?.detail }));
      })
    );
  }
}