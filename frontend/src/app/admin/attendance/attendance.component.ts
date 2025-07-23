import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from 'src/app/core/services/auth.service';
import { Attendance } from 'src/app/core/interfaces/attendance.interface';

@Component({
  selector: 'app-attendance',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './attendance.component.html',
  styleUrls: ['./attendance.component.css']
})
export class AttendanceComponent implements OnInit {
  attendanceLogs: Attendance[] = [];
  filterDate: string = new Date().toISOString().split('T')[0]; // Default to today
  errorMessage: string | null = null;

  constructor(private http: HttpClient, private authService: AuthService) {}

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

    this.http.get<{ logs: Attendance[] }>(`http://localhost:8000/admin/attendance/logs?date=${this.filterDate}`, { headers }).subscribe({
      next: (data) => {
        this.attendanceLogs = data.logs;
        console.log('Loaded Attendance Logs:', this.attendanceLogs);
      },
      error: (err) => {
        console.error('Error loading attendance logs:', err);
        this.errorMessage = err.error?.detail || 'Error loading attendance logs';
      }
    });
  }

  onDateChange(event: Event) {
    const target = event.target as HTMLInputElement;
    this.filterDate = target.value;
    this.loadAttendanceLogs();
  }
}