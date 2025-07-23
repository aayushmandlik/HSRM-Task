import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from 'src/app/core/services/auth.service';
import { Attendance } from 'src/app/core/interfaces/attendance.interface';

// Define the expected API response structure
interface ApiResponse {
  message: string;
}

@Component({
  selector: 'app-employee-attendance',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './employee-attendance.component.html',
  styleUrls: ['./employee-attendance.component.css']
})
export class EmployeeAttendanceComponent implements OnInit {
  attendanceLogs: Attendance[] = [];
  errorMessage: string | null = null;
  attendanceForm: FormGroup;
  successMessage: string | null = null;

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private fb: FormBuilder
  ) {
    this.attendanceForm = this.fb.group({
      action: ['', Validators.required]
    });
  }

  ngOnInit() {
    this.loadAttendanceLogs();
  }

  loadAttendanceLogs() {
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token available. Please log in.');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<{ logs: Attendance[] }>(`http://localhost:8000/attendance/logs/me`, { headers }).subscribe({
      next: (data) => {
        this.attendanceLogs = data.logs;
        console.log('Loaded My Attendance Logs:', this.attendanceLogs);
      },
      error: (err) => {
        console.error('Error loading attendance logs:', err);
        this.errorMessage = err.error?.detail || 'Error loading attendance logs';
      }
    });
  }

  onSubmit() {
    const token = this.authService.getToken();
    if (!token) {
      this.errorMessage = 'No token available. Please log in.';
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    const action = this.attendanceForm.get('action')?.value;

    let url = '';
    switch (action) {
      case 'checkin':
        url = 'http://localhost:8000/attendance/checkin';
        break;
      case 'checkout':
        url = 'http://localhost:8000/attendance/checkout';
        break;
      case 'breakin':
        url = 'http://localhost:8000/attendance/breakin';
        break;
      case 'breakout':
        url = 'http://localhost:8000/attendance/breakout';
        break;
      default:
        this.errorMessage = 'Invalid action selected.';
        return;
    }

    this.http.post<ApiResponse>(url, {}, { headers }).subscribe({
      next: (response) => {
        this.successMessage = response.message; // Now type-safe
        this.errorMessage = null;
        this.attendanceForm.reset();
        this.loadAttendanceLogs(); // Refresh logs after action
      },
      error: (err) => {
        console.error('Error performing action:', err);
        this.errorMessage = err.error?.detail || 'Error performing action';
        this.successMessage = null;
      }
    });
  }
}