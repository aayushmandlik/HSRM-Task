import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterModule } from '@angular/router';
import { AuthService } from 'src/app/core/services/auth.service';
@Component({
  selector: 'app-user-profile',
  standalone: true,
  imports: [CommonModule,RouterLink,RouterModule],
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.css']
})
export class UserProfileComponent {
  selectedSection: string = 'employees';

  constructor(private authservice: AuthService){}

  selectSection(section: string): void {
    this.selectedSection = section;
  }

  logout():void {
    this.authservice.logout();
  }
  
}