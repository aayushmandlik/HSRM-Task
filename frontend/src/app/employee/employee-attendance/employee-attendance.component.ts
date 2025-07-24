import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Attendance } from 'src/app/core/interfaces/attendance.interface';
import { AttendanceService } from 'src/app/core/services/attendance.service';
import { AuthService } from 'src/app/core/services/auth.service';
import { Observable } from 'rxjs';

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
  successMessage: string | null = null;
  attendanceForm: FormGroup;

  constructor(
    private attendanceService: AttendanceService,
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
    this.attendanceService.getMyAttendanceLogs().subscribe({
      next: (data) => {
        this.attendanceLogs = data;
        console.log('Loaded My Attendance Logs:', this.attendanceLogs);
        this.errorMessage = null;
      },
      error: (err) => {
        console.error('Error loading my attendance logs:', err.message);
        this.errorMessage = `Error loading my attendance logs: ${err.message || 'Unknown error'}`;
      }
    });
  }

  onSubmit() {
    if (this.attendanceForm.valid) {
      const action = this.attendanceForm.get('action')?.value;
      let request: Observable<{ message: string }>;

      switch (action) {
        case 'checkin':
          request = this.attendanceService.checkIn();
          break;
        case 'checkout':
          request = this.attendanceService.checkOut();
          break;
        case 'breakin':
          request = this.attendanceService.breakIn();
          break;
        case 'breakout':
          request = this.attendanceService.breakOut();
          break;
        default:
          this.errorMessage = 'Error performing action: Invalid action selected';
          return;
      }

      request.subscribe({
        next: (response) => {
          this.successMessage = response.message;
          this.errorMessage = null;
          this.attendanceForm.reset();
          this.loadAttendanceLogs();
        },
        error: (err) => {
          console.error('Error performing action:', err.message);
          this.errorMessage = `Error performing action: ${err.message || 'Unknown error'}`;
          this.successMessage = null;
        }
      });
    }
  }
}