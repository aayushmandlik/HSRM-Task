import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from 'src/app/core/services/auth.service';
import { LeaveCreate, LeaveResponse, LeaveUpdateStatus } from 'src/app/core/interfaces/leave.interface';

@Component({
  selector: 'app-leave',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './leave.component.html',
  styleUrls: ['./leave.component.css']
})
export class LeaveComponent implements OnInit {
  leaveForm: FormGroup;
  pendingLeaves: LeaveResponse[] = [];
  approvedRejectedLeaves: LeaveResponse[] = [];
  errorMessage: string | null = null;
  successMessage: string | null = null;
  isModalOpen: boolean = false;
  selectedLeaveId: string | null = null;
  tooltipVisible: boolean = false;
  hoveredLeaveId: string | null = null;
  tooltipText: string = '';

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private authService: AuthService
  ) {
    this.leaveForm = this.fb.group({
      status: ['', [Validators.required]],
      approved_by: ['', [Validators.required]]
    });
  }

  ngOnInit() {
    this.loadPendingLeaveRequests();
    this.loadApprovedRejectedLeaveRequests();
  }

  loadPendingLeaveRequests() {
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token available. Please log in.');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<LeaveResponse[]>(`http://localhost:8000/admin/leave/pendingrequests`, { headers }).subscribe({
      next: (data) => {
        this.pendingLeaves = data;
        console.log('Loaded Pending Leave Requests with IDs:', data.map(leave => ({ _id: leave._id, employee_name: leave.employee_name })));
      },
      error: (err) => console.error('Error loading pending leave requests:', err)
    });
  }

  loadApprovedRejectedLeaveRequests() {
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token available. Please log in.');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<LeaveResponse[]>(`http://localhost:8000/admin/leave/leaverequests`, { headers }).subscribe({
      next: (data) => {
        this.approvedRejectedLeaves = data.filter(leave => leave.status !== 'pending');
        console.log('Loaded Approved/Rejected Leave Requests:', this.approvedRejectedLeaves);
      },
      error: (err) => console.error('Error loading leave requests:', err)
    });
  }

  openModal(leaveId: string) {
    console.log('Attempting to open modal with leaveId:', leaveId); // Debug the incoming leaveId
    if (!leaveId) {
      console.error('Invalid leaveId passed to openModal:', leaveId);
      return;
    }
    this.selectedLeaveId = leaveId;
    this.isModalOpen = true;
    this.leaveForm.reset(); // Reset form to clear previous values
    this.successMessage = null;
    this.errorMessage = null;
  }

  closeModal() {
    this.isModalOpen = false;
    this.selectedLeaveId = null;
    this.leaveForm.reset();
    this.successMessage = null;
    this.errorMessage = null;
  }

  updateLeaveStatus() {
    console.log('Form value:', this.leaveForm.value); // Debug form value
    console.log('Selected Leave ID:', this.selectedLeaveId); // Debug selectedLeaveId
    if (this.leaveForm.valid && this.selectedLeaveId) {
      const leaveUpdate: LeaveUpdateStatus = this.leaveForm.value;
      const token = this.authService.getToken();
      if (!token) {
        console.error('No token available. Please log in.');
        return;
      }
      const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

      console.log('Sending update request:', { leaveId: this.selectedLeaveId, data: leaveUpdate }); // Debug request

      this.http.put<LeaveResponse>(`http://localhost:8000/admin/leave/${this.selectedLeaveId}/status`, leaveUpdate, { headers }).subscribe({
        next: (response) => {
          console.log('Leave status updated successfully:', response);
          this.successMessage = 'Leave status updated successfully!';
          
          // Remove from pendingLeaves if no longer pending
          this.pendingLeaves = this.pendingLeaves.filter(leave => leave._id !== this.selectedLeaveId);
          
          // Add to approvedRejectedLeaves if status is approved or rejected
          if (response.status !== 'pending') {
            const existingIndex = this.approvedRejectedLeaves.findIndex(leave => leave._id === response._id);
            if (existingIndex !== -1) {
              this.approvedRejectedLeaves[existingIndex] = response;
            } else {
              this.approvedRejectedLeaves.push(response);
            }
          }

          this.loadPendingLeaveRequests();
          this.loadApprovedRejectedLeaveRequests(); // Refresh both lists
          this.closeModal();
        },
        error: (err) => {
          console.error('Error updating leave status:', err);
          this.errorMessage = err.error?.detail || 'Error updating leave status';
        }
      });
    } else {
      console.log('Form is invalid or no leave selected:', this.leaveForm.value, this.selectedLeaveId); // Debug invalid case
      if (!this.leaveForm.valid) {
        console.log('Form errors:', this.leaveForm.errors);
        this.leaveForm.markAllAsTouched(); // Force validation messages to show
      }
      if (!this.selectedLeaveId) {
        console.error('No leave selected - this should not happen if openModal worked');
      }
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
    return this.pendingLeaves.length;
  }

  get approvedLeavesCount(): number {
    return this.approvedRejectedLeaves.filter(leave => leave.status === 'approved').length;
  }

  get totalLeavesTaken(): number {
    return this.approvedRejectedLeaves
      .filter(leave => leave.status === 'approved')
      .reduce((sum, leave) => sum + leave.days, 0);
  }

  get remainingLeaves(): number {
    const initialLeaves = 20;
    return initialLeaves - this.totalLeavesTaken;
  }
}