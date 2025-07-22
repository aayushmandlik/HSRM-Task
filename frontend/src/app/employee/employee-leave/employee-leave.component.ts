import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from 'src/app/core/services/auth.service';
import { LeaveCreate, LeaveResponse } from 'src/app/core/interfaces/leave.interface';

@Component({
  selector: 'app-employee-leave',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './employee-leave.component.html',
  styleUrls: ['./employee-leave.component.css']
})
export class EmployeeLeaveComponent implements OnInit {
  leaveForm: FormGroup;
  leaves: LeaveResponse[] = [];
  errorMessage: string | null = null;
  successMessage: string | null = null;
  isModalOpen: boolean = false;
  tooltipVisible: boolean = false;
  hoveredLeaveId: string | null = null;
  tooltipText: string = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private authService: AuthService
  ) {
    this.leaveForm = this.fb.group({
      start_date: ['', [Validators.required]],
      end_date: ['', [Validators.required]],
      leave_type: ['', [Validators.required]],
      reason: ['', [Validators.required]]
    });
  }

  ngOnInit() {
    this.loadMyLeaveRequests();
  }

  loadMyLeaveRequests() {
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token available. Please log in.');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<LeaveResponse[]>(`http://localhost:8000/Emp_leave/my-requests`, { headers }).subscribe({
      next: (data) => {
        this.leaves = data;
        console.log('Loaded My Leave Requests:', data);
      },
      error: (err) => console.error('Error loading leave requests:', err)
    });
  }

  onSubmitLeave() {
    if (this.leaveForm.valid) {
      const leaveData: LeaveCreate = this.leaveForm.value;
      const token = this.authService.getToken();
      if (!token) {
        console.error('No token available. Please log in.');
        return;
      }
      const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

      // Only create new leave
      this.http.post<LeaveResponse>(`http://localhost:8000/Emp_leave/request`, leaveData, { headers }).subscribe({
        next: (response) => {
          console.log('Leave request submitted:', response);
          this.successMessage = 'Leave request submitted successfully!';
          this.leaveForm.reset();
          this.loadMyLeaveRequests();
          this.closeModal();
        },
        error: (err) => {
          console.error('Error submitting leave request:', err);
          this.errorMessage = err.error.detail || 'Error submitting leave request';
        }
      });
    }
  }

  openModal() {
    this.isModalOpen = true;
    this.successMessage = null;
    this.errorMessage = null;
    this.leaveForm.reset();
  }

  closeModal() {
    this.isModalOpen = false;
    this.leaveForm.reset();
    this.successMessage = null;
    this.errorMessage = null;
  }

  deleteLeave(leaveId: string) {
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token available. Please log in.');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    if (confirm('Are you sure you want to delete this leave request?')) {
      this.http.delete(`http://localhost:8000/Emp_leave/${leaveId}`, { headers }).subscribe({
        next: () => {
          console.log('Leave deleted:', leaveId);
          this.successMessage = 'Leave deleted successfully!';
          this.loadMyLeaveRequests();
        },
        error: (err) => {
          console.error('Error deleting leave:', err);
          this.errorMessage = err.error.detail || 'Error deleting leave';
        }
      });
    }
  }

  showTooltip(leaveId: string, reason: string) {
    this.hoveredLeaveId = leaveId;
    this.tooltipText = reason || 'No reason provided';
    this.tooltipVisible = true;
  }

  hideTooltip() {
    this.tooltipVisible = false;
    this.hoveredLeaveId = null;
    this.tooltipText = '';
  }

  @HostListener('document:click', ['$event'])
  onClick(event: MouseEvent) {
    if (this.tooltipVisible && !this.isModalOpen) {
      const tooltip = document.querySelector('.absolute.bg-gray-800');
      if (tooltip && !tooltip.contains(event.target as Node)) {
        this.hideTooltip();
      }
    }
  }

  get pendingLeavesCount(): number {
    return this.leaves.filter(leave => leave.status === 'pending').length;
  }

  get approvedLeavesCount(): number {
    return this.leaves.filter(leave => leave.status === 'approved').length;
  }

  get totalLeavesTaken(): number {
    return this.leaves
      .filter(leave => leave.status === 'approved') // Only count approved leaves
      .reduce((sum, leave) => sum + leave.days, 0); // Sum the days of approved leaves
  }

  get remainingLeaves(): number {
    const initialLeaves = 20; // Assuming initial leave balance is 20 days
    return initialLeaves - this.totalLeavesTaken; // Remaining = Initial - Total Taken
  }
}