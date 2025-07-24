import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { EmployeeCreate, EmployeeUpdate } from '../interfaces/employee.interface';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class EmployeeService {
  private baseUrl = 'http://localhost:8000/employee';

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    if (!token) {
      throw new Error('No token available. Please log in.');
    }
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getAllEmployees(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/getall`, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error fetching employees:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error fetching employees', detail: error.error?.detail }));
      })
    );
  }

  createEmployee(employeeData: EmployeeCreate): Observable<any> {
    return this.http.post(`${this.baseUrl}/create`, employeeData, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error creating employee:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error creating employee', detail: error.error?.detail }));
      })
    );
  }

  updateEmployee(empCode: string, employeeData: EmployeeUpdate): Observable<any> {
    return this.http.put(`${this.baseUrl}/${empCode}`, employeeData, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error updating employee:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error updating employee', detail: error.error?.detail }));
      })
    );
  }

  deleteEmployee(empCode: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${empCode}`, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error deleting employee:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error deleting employee', detail: error.error?.detail }));
      })
    );
  }
}