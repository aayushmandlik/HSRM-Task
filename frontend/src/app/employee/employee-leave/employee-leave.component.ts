import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { LeaveCreate, LeaveResponse, LeaveUpdate } from 'src/app/core/interfaces/leave.interface';
import { LeaveService } from 'src/app/core/services/leave.service';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-employee-leave',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './employee-leave.component.html',
  styleUrls: ['./employee-leave.component.css']
})
export class EmployeeLeaveComponent implements OnInit {
  leaveForm: FormGroup;
  updateForm: FormGroup;
  leaves: LeaveResponse[] = [];
  errorMessage: string | null = null;
  successMessage: string | null = null;
  isModalOpen: boolean = false;
  selectedLeaveId: string | null = null;

  constructor(
    private fb: FormBuilder,
    private leaveService: LeaveService,
    private authService: AuthService
  ) {
    this.leaveForm = this.fb.group({
      start_date: ['', [Validators.required]],
      end_date: ['', [Validators.required]],
      leave_type: ['', [Validators.required]],
      reason: ['', [Validators.required]]
    });
    this.updateForm = this.fb.group({
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
    this.leaveService.getMyLeaveRequests().subscribe({
      next: (data) => {
        this.leaves = data;
        console.log('Loaded My Leave Requests:', data);
      },
      error: (err) => {
        console.error('Error loading my leave requests:', err.message);
        this.errorMessage = `Error loading my leave requests: ${err.message || 'Unknown error'}`;
      }
    });
  }

  onSubmitLeave() {
    if (this.leaveForm.valid) {
      const leaveData: LeaveCreate = this.leaveForm.value;
      this.leaveService.createLeaveRequest(leaveData).subscribe({
        next: (response) => {
          console.log('Leave request submitted:', response);
          this.successMessage = 'Leave request submitted successfully!';
          this.leaveForm.reset();
          this.loadMyLeaveRequests();
          this.closeModal();
        },
        error: (err) => {
          console.error('Error submitting leave request:', err.message);
          this.errorMessage = `Error submitting leave request: ${err.message || 'Unknown error'}`;
        }
      });
    }
  }

  openModal(leaveId: string | null = null) {
    this.isModalOpen = true;
    this.successMessage = null;
    this.errorMessage = null;
    this.selectedLeaveId = leaveId;
    this.leaveForm.reset();
    this.updateForm.reset();

    if (leaveId && this.leaves.length > 0) {
      const leave = this.leaves.find(l => l._id === leaveId);
      if (leave) {
        console.log('Pre-filling with:', leave);
        if (this.selectedLeaveId) {
          this.updateForm.patchValue({
            start_date: leave.start_date,
            end_date: leave.end_date,
            leave_type: leave.leave_type,
            reason: leave.reason
          });
        } else {
          this.leaveForm.patchValue({
            start_date: leave.start_date,
            end_date: leave.end_date,
            leave_type: leave.leave_type,
            reason: leave.reason
          });
        }
      } else {
        console.warn('Leave not found for id:', leaveId);
      }
    }
  }

  closeModal() {
    this.isModalOpen = false;
    this.selectedLeaveId = null;
    this.leaveForm.reset();
    this.updateForm.reset();
    this.successMessage = null;
    this.errorMessage = null;
  }

  onSubmitUpdate() {
    if (this.updateForm.valid && this.selectedLeaveId) {
      const updateData: LeaveUpdate = this.updateForm.value;
      this.leaveService.updateLeaveRequest(this.selectedLeaveId, updateData).subscribe({
        next: (response) => {
          console.log('Leave updated:', response);
          this.successMessage = 'Leave updated successfully!';
          this.loadMyLeaveRequests();
          this.closeModal();
        },
        error: (err) => {
          console.error('Error updating leave:', err.message);
          this.errorMessage = `Error updating leave: ${err.message || 'Unknown error'}`;
        }
      });
    }
  }

  deleteLeave(leaveId: string) {
    if (confirm('Are you sure you want to delete this leave request?')) {
      this.leaveService.deleteLeaveRequest(leaveId).subscribe({
        next: () => {
          console.log('Leave deleted:', leaveId);
          this.successMessage = 'Leave deleted successfully!';
          this.loadMyLeaveRequests();
        },
        error: (err) => {
          console.error('Error deleting leave:', err.message);
          this.errorMessage = `Error deleting leave: ${err.message || 'Unknown error'}`;
        }
      });
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
      .filter(leave => leave.status === 'approved')
      .reduce((sum, leave) => sum + leave.days, 0);
  }

  get remainingLeaves(): number {
    const initialLeaves = 20;
    return initialLeaves - this.totalLeavesTaken;
  }
}