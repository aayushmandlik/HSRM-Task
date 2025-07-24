import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Attendance } from 'src/app/core/interfaces/attendance.interface';
import { AttendanceService } from 'src/app/core/services/attendance.service';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-attendance',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './attendance.component.html',
  styleUrls: ['./attendance.component.css']
})
export class AttendanceComponent implements OnInit {
  attendanceLogs: Attendance[] = [];
  filterDate: string = new Date().toISOString().split('T')[0]; // Default to today
  errorMessage: string | null = null;

  constructor(private attendanceService: AttendanceService, private authService: AuthService) {}

  ngOnInit() {
    this.loadAttendanceLogs();
  }

  loadAttendanceLogs() {
    this.attendanceService.getAttendanceLogs(this.filterDate).subscribe({
      next: (data) => {
        this.attendanceLogs = data;
        console.log('Loaded Attendance Logs:', this.attendanceLogs);
        this.errorMessage = null;
      },
      error: (err) => {
        console.error('Error loading attendance logs:', err.message);
        this.errorMessage = `Error loading attendance logs: ${err.message || 'Unknown error'}`;
      }
    });
  }

  onDateChange(event: Event) {
    const target = event.target as HTMLInputElement;
    this.filterDate = target.value;
    this.loadAttendanceLogs();
  }

  get getTotalEmployees():number{
    return this.attendanceLogs.length;
  }

  get presentEmployees():number{
    return this.attendanceLogs.filter(present => present.status === "Present").length;
  }

  get absentEmployees():number{
    return this.attendanceLogs.filter(absent => absent.status === "Absent").length;
  }
}