import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { TaskOut, TaskCreate, TaskUpdate, TaskComment } from '../interfaces/task.interface';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class TaskService {
  private baseUrl = 'http://localhost:8000/tasks';

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    if (!token) {
      throw new Error('No token available. Please log in.');
    }
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getAllTasks(): Observable<TaskOut[]> {
    return this.http.get<TaskOut[]>(`${this.baseUrl}/`, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error fetching tasks:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error fetching tasks', detail: error.error?.detail }));
      })
    );
  }

  createTask(taskData: TaskCreate): Observable<TaskOut> {
    return this.http.post<TaskOut>(`${this.baseUrl}/`, taskData, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error creating task:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error creating task', detail: error.error?.detail }));
      })
    );
  }

  updateTask(taskId: string, taskData: TaskUpdate): Observable<TaskOut> {
    return this.http.put<TaskOut>(`${this.baseUrl}/${taskId}`, taskData, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error updating task:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error updating task', detail: error.error?.detail }));
      })
    );
  }

  deleteTask(taskId: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${taskId}`, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error deleting task:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error deleting task', detail: error.error?.detail }));
      })
    );
  }

  getMyTasks(): Observable<TaskOut[]> {
    return this.http.get<TaskOut[]>(`${this.baseUrl}/my`, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error fetching tasks:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error fetching tasks', detail: error.error?.detail }));
      })
    );
  }

  updateTaskStatus(taskId: string, status: string): Observable<TaskOut> {
    return this.http.patch<TaskOut>(`${this.baseUrl}/${taskId}/status`, { status }, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error updating task status:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error updating task status', detail: error.error?.detail }));
      })
    );
  }

  addComment(taskId: string, commentData: TaskComment): Observable<TaskOut> {
    return this.http.post<TaskOut>(`${this.baseUrl}/${taskId}/comment`, commentData, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Error adding comment:', error);
        return throwError(() => ({ message: error.error?.detail || 'Error adding comment', detail: error.error?.detail }));
      })
    );
  }
}