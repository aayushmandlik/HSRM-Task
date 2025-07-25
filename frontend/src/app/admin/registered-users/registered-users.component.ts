import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TokenPayload } from 'src/app/core/interfaces/user.interface';
import { RegisteredusersService } from 'src/app/core/services/registeredusers.service';
import { AuthService } from 'src/app/core/services/auth.service';

@Component({
  selector: 'app-registered-users',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './registered-users.component.html',
  styleUrls: ['./registered-users.component.css']
})
export class RegisteredUsersComponent implements OnInit {
  registeredusersadmins: TokenPayload[] = []

  constructor(private registeredService: RegisteredusersService, private authService: AuthService){}


  ngOnInit(): void {
    this.loadRegisteredUsersaAdmin();
  }

  loadRegisteredUsersaAdmin(){
    this.registeredService.getAllRegistered().subscribe({
      next: (data)=>{
        this.registeredusersadmins = data;
        console.log("Loaded Users: ",data)
      },
      error: (err) => {
        console.log("Error loading users: ",err.message)
      }
    })
  }
  
}
