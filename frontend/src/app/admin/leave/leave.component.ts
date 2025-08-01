import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { LeaveResponse, LeaveUpdateStatus } from 'src/app/core/interfaces/leave.interface';
import { LeaveService } from 'src/app/core/services/leave.service';
import { AuthService } from 'src/app/core/services/auth.service';

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
  filteredApprovedRejectedLeaves: LeaveResponse[] = [];
  errorMessage: string | null = null;
  successMessage: string | null = null;
  isModalOpen: boolean = false;
  selectedLeaveId: string | null = null;
  tooltipVisible: boolean = false;
  hoveredLeaveId: string | null = null;
  tooltipText: string = '';
  searchTerm: string = '';
  statusFilter: string = '';

  constructor(
    private fb: FormBuilder,
    private leaveService: LeaveService,
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
    this.leaveService.getPendingLeaveRequests().subscribe({
      next: (data) => {
        this.pendingLeaves = data;
        console.log('Loaded Pending Leave Requests with IDs:', data.map(leave => ({ _id: leave._id, employee_name: leave.employee_name })));
      },
      error: (err) => {
        console.error('Error loading pending leave requests:', err.message);
        this.errorMessage = `Error loading pending leave requests: ${err.message || 'Unknown error'}`;
      }
    });
  }

  loadApprovedRejectedLeaveRequests() {
    this.leaveService.getApprovedRejectedLeaveRequests().subscribe({
      next: (data) => {
        this.approvedRejectedLeaves = data.filter(leave => leave.status !== 'pending');
        this.filteredApprovedRejectedLeaves = [...this.approvedRejectedLeaves];
        console.log('Loaded Approved/Rejected Leave Requests:', this.approvedRejectedLeaves);
      },
      error: (err) => {
        console.error('Error loading approved/rejected leave requests:', err.message);
        this.errorMessage = `Error loading approved/rejected leave requests: ${err.message || 'Unknown error'}`;
      }
    });
  }

  openModal(leaveId: string) {
    if (!leaveId) {
      console.error('Invalid leaveId passed to openModal:', leaveId);
      this.errorMessage = 'Error: Invalid leave ID';
      return;
    }
    this.selectedLeaveId = leaveId;
    this.isModalOpen = true;
    this.leaveForm.reset();
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
    if (this.leaveForm.valid && this.selectedLeaveId) {
      const leaveUpdate: LeaveUpdateStatus = this.leaveForm.value;
      this.leaveService.updateLeaveStatus(this.selectedLeaveId, leaveUpdate).subscribe({
        next: (response) => {
          console.log('Leave status updated successfully:', response);
          this.successMessage = 'Leave status updated successfully!';
          this.pendingLeaves = this.pendingLeaves.filter(leave => leave._id !== this.selectedLeaveId);
          if (response.status !== 'pending') {
            const existingIndex = this.approvedRejectedLeaves.findIndex(leave => leave._id === response._id);
            if (existingIndex !== -1) {
              this.approvedRejectedLeaves[existingIndex] = response;
            } else {
              this.approvedRejectedLeaves.push(response);
            }
            this.applyFilters();
          }
          this.loadPendingLeaveRequests();
          this.loadApprovedRejectedLeaveRequests();
          this.closeModal();
        },
        error: (err) => {
          console.error('Error updating leave status:', err.message);
          this.errorMessage = `Error updating leave status: ${err.message || 'Unknown error'}`;
        }
      });
    } else {
      if (!this.leaveForm.valid) {
        console.log('Form errors:', this.leaveForm.errors);
        this.leaveForm.markAllAsTouched();
      }
      if (!this.selectedLeaveId) {
        console.error('No leave selected');
        this.errorMessage = 'Error: No leave selected';
      }
    }
  }


  get pendingLeavesCount(): number {
    return this.pendingLeaves.length;
  }

  get approvedLeavesCount(): number {
    return this.approvedRejectedLeaves.filter(leave => leave.status === 'approved').length;
  }

  get rejectedLeavesCount(): number {
    return this.approvedRejectedLeaves.filter(leave => leave.status === "rejected").length;
  }

  get totalLeavesTaken(): number {
    return this.approvedRejectedLeaves
      .filter(leave => leave.status === 'approved')
      .reduce((sum, leave) => sum + leave.days, 0);
  }

  get remainingLeaves(): number {
    const initialLeaves = 30;
    return initialLeaves - this.totalLeavesTaken;
  }

  getLeaveCount(leaveType: string): number {
    return this.approvedRejectedLeaves.filter(leave => leave.leave_type === leaveType).length;
  }

  onSearch(event: Event) {
    const input = event.target as HTMLInputElement;
    this.searchTerm = input.value.toLowerCase();
    this.applyFilters();
  }

  onFilterStatus(event: Event) {
    const select = event.target as HTMLSelectElement;
    this.statusFilter = select.value;
    this.applyFilters();
  }

  applyFilters() {
    this.filteredApprovedRejectedLeaves = this.approvedRejectedLeaves.filter(leave => {
      const matchesSearch = leave.employee_name.toLowerCase().includes(this.searchTerm);
      const matchesStatus = !this.statusFilter || leave.status === this.statusFilter;
      return matchesSearch && matchesStatus;
    });
  }
}