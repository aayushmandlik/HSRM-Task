import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { EmployeeCreate } from 'src/app/core/interfaces/employee.interface';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-employees',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HttpClientModule],
  templateUrl: './employees.component.html',
  styleUrls: ['./employees.component.css']
})
export class EmployeesComponent implements OnInit {
  isModalOpen = false;
  employeeForm: FormGroup;
  employees: any[] = [];
  ttlempicon: string=""

  constructor(private fb: FormBuilder, private http: HttpClient, private authService: AuthService) {
    this.employeeForm = this.fb.group({
      user_id: ['', [Validators.required]],
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
      reporting_manager: ['']
    });
    this.ttlempicon = "src/assets/ttlempicon.png"
  }

  ngOnInit() {
    this.loadEmployees();
  }

  openModal() {
    this.isModalOpen = true;
  }

  closeModal() {
    this.isModalOpen = false;
    this.employeeForm.reset();
  }

  onSubmit() {
    if (this.employeeForm.valid) {
      const employeeData: EmployeeCreate = this.employeeForm.value;
      const token = this.authService.getToken();
      if (!token) {
        console.error('No token available. Please log in.');
        return;
      }
      const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

      this.http.post('http://localhost:8000/employee/create', employeeData, { headers }).subscribe({
        next: (response) => {
          console.log('Employee added:', response);
          this.closeModal();
          this.loadEmployees();
        },
        error: (err) => console.error('Error adding employee:', err)
      });
    }
  }

  loadEmployees() {
    const token = this.authService.getToken();
    if (!token) {
      console.error('No token available. Please log in as an admin.');
      return;
    }
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);

    this.http.get<any[]>('http://localhost:8000/employee/getall', { headers }).subscribe({
      next: (data) => {
        this.employees = data;
      },
      error: (err) => console.error('Error loading employees:', err)
    });
  }
}