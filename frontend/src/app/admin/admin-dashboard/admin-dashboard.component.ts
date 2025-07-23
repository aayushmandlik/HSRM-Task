// import { Component, OnInit } from '@angular/core';
// import { CommonModule } from '@angular/common';
// import { AuthService } from '../../core/services/auth.service';
// import { RouterLink, RouterModule } from '@angular/router';

// @Component({
//   selector: 'app-admin-dashboard',
//   standalone: true,
//   imports: [CommonModule, RouterLink, RouterModule],
//   templateUrl: './admin-dashboard.component.html',
//   styleUrls: ['./admin-dashboard.component.css']
// })
// export class AdminDashboardComponent implements OnInit {
//   admin: any;

//   constructor(private authService: AuthService) {}

//   ngOnInit(): void {
//     this.admin = this.authService.getCurrentUser();
//   }

//   selectedSection: string = 'employees';

//   selectSection(section: string): void {
//     this.selectedSection = section;
//   }

//   logout(): void {
//     this.authService.logout();
//   }
// }


import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterModule } from '@angular/router';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterModule],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent {
  // selectedSection: string = 'dashboard';

  constructor(private authservice: AuthService){}

  // selectSection(section: string): void {
  //   this.selectedSection = section;
  // }

  logout(): void{
    this.authservice.logout();
  }
}