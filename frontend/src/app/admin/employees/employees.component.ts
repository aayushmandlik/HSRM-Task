import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { EmployeeCreate, EmployeeOut, EmployeeUpdate } from 'src/app/core/interfaces/employee.interface';
import { EmployeeService } from 'src/app/core/services/employee.service';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-employees',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './employees.component.html',
  styleUrls: ['./employees.component.css']
})
export class EmployeesComponent implements OnInit {
  isModalOpen = false;
  employeeForm: FormGroup;
  employees: EmployeeOut[] = [];
  filteredEmployees: EmployeeOut[] = [];
  ttlempicon: string = '';
  selectedEmployeeId: string | null = null;
  errorMessage: string | null = null;
  searchTerm: string = '';
  statusFilter: string = '';
  departmentFilter: string = '';

  constructor(
    private fb: FormBuilder,
    private employeeService: EmployeeService,
    private authService: AuthService
  ) {
    this.employeeForm = this.fb.group({
      emp_code: ['', [Validators.required]],
      name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', [Validators.required]],
      gender: [''],
      dob: [''],
      address: [''],
      profile_image: [''],
      department: ['', [Validators.required]],
      designation: ['', [Validators.required]],
      date_of_joining: ['', [Validators.required]],
      location: ['', [Validators.required]],
      reporting_manager_id: [''],
      reporting_manager: [''],
      status: ['']
    });
  }

  ngOnInit() {
    this.loadEmployees();
  }

  openModal(empCode: string | null = null) {
    this.isModalOpen = true;
    this.selectedEmployeeId = empCode;
    this.employeeForm.reset();
    this.errorMessage = null;

    if (empCode && this.employees.length > 0) {
      const employee = this.employees.find(emp => emp.emp_code === empCode);
      if (employee) {
        console.log('Pre-filling with:', employee);
        this.employeeForm.patchValue({
          emp_code: employee.emp_code || '',
          name: employee.name || '',
          email: employee.email || '',
          phone: employee.phone || '',
          gender: employee.gender || '',
          dob: employee.dob || '',
          address: employee.address || '',
          profile_image: employee.profile_image || '',
          department: employee.department || '',
          designation: employee.designation || '',
          date_of_joining: employee.date_of_joining || '',
          location: employee.location || '',
          reporting_manager_id: employee.reporting_manager_id || '',
          reporting_manager: employee.reporting_manager || '',
          status: employee.status || ''
        });
      } else {
        console.warn('Employee not found for emp_code:', empCode);
      }
    }
  }

  closeModal() {
    this.isModalOpen = false;
    this.employeeForm.reset();
    this.selectedEmployeeId = null;
    this.errorMessage = null;
  }

  onSubmit() {
    if (this.employeeForm.valid) {
      const employeeData: EmployeeCreate = this.employeeForm.value;
      console.log('Submitting Data:', employeeData);

      if (this.selectedEmployeeId) {
        this.employeeService.updateEmployee(this.selectedEmployeeId, employeeData).subscribe({
          next: (response) => {
            console.log('Employee updated:', response);
            this.closeModal();
            this.loadEmployees();
          },
          error: (err) => {
            console.error('Error updating employee:', err.message);
            this.errorMessage = `Error updating employee: ${err.message || 'Unknown error'}`;
          }
        });
      } else {
        this.employeeService.createEmployee(employeeData).subscribe({
          next: (response) => {
            console.log('Employee added:', response);
            this.closeModal();
            this.loadEmployees();
          },
          error: (err) => {
            console.error('Error adding employee:', err.message);
            this.errorMessage = `Error adding employee: ${err.message || 'Unknown error'}`;
          }
        });
      }
    }
  }

  loadEmployees() {
    this.employeeService.getAllEmployees().subscribe({
      next: (data) => {
        this.employees = data;
        this.filteredEmployees = [...this.employees];
        console.log('Loaded Employees:', data);
      },
      error: (err) => {
        console.error('Error loading employees:', err.message);
        this.errorMessage = `Error loading employees: ${err.message || 'Unknown error'}`;
      }
    });
  }

  deleteEmployee(empCode: string) {
    if(confirm('Are you sure you want to delete this leave request?')){
      this.employeeService.deleteEmployee(empCode).subscribe({
        next: (response) => {
          console.log('Employee deleted:', response);
          this.loadEmployees();
        },
        error: (err) => {
          console.error('Error deleting employee:', err.message);
          this.errorMessage = `Error deleting employee: ${err.message || 'Unknown error'}`;
        }
      });
    }
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

  onFilterDepartment(event: Event) {
    const select = event.target as HTMLSelectElement;
    this.departmentFilter = select.value;
    this.applyFilters();
  }

  applyFilters() {
    this.filteredEmployees = this.employees.filter(employee => {
      const matchesSearch = employee.name.toLowerCase().includes(this.searchTerm);
      const matchesStatus = !this.statusFilter || employee.status === this.statusFilter;
      const matchesDepartment = !this.departmentFilter || employee.department === this.departmentFilter;
      return matchesSearch && matchesStatus && matchesDepartment;
    });
  }

  get getActiveCount(): number {
    return this.employees.filter(employee => employee.status === 'Active').length;
  }

  get getInactiveCount(): number {
    return this.employees.filter(employee => employee.status === 'InActive').length;
  }

  get getNewJoinersCount(): number {
    const oneMonthAgo = new Date('2025-06-22');
    return this.employees.filter(employee => {
      const joinDate = new Date(employee.date_of_joining);
      return joinDate >= oneMonthAgo && joinDate <= new Date();
    }).length;
  }
}