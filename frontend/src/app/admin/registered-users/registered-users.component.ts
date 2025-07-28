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
  searchTerm: string = '';
  filterRole: string | null = null;
  filteredUsers: TokenPayload[] = []
  registeredusersadmins: TokenPayload[] = []

  constructor(private registeredService: RegisteredusersService, private authService: AuthService){}


  ngOnInit(): void {
    this.loadRegisteredUsersaAdmin();
  }

  loadRegisteredUsersaAdmin(){
    this.registeredService.getAllRegistered().subscribe({
      next: (data)=>{
        this.registeredusersadmins = data;
        this.filterUsers();
        console.log("Loaded Users: ",data)
      },
      error: (err) => {
        console.log("Error loading users: ",err.message)
      }
    })
  }

  onSearch(event: Event) {
    this.searchTerm = (event.target as HTMLInputElement).value;
    this.filterUsers();
  }


  onFilterRole(event: Event) {
    this.filterRole = (event.target as HTMLInputElement).value;
    this.filterUsers();
  }

  filterUsers(){
    this.filteredUsers = this.registeredusersadmins.filter(user => {
      const matchesSearch = !this.searchTerm || user.name.toLowerCase().includes(this.searchTerm.toLowerCase()) 
      || user.email.toLowerCase().includes(this.searchTerm.toLowerCase())
      
      const matchesRole = !this.filterRole || user.role == this.filterRole

      return matchesSearch && matchesRole
    })
  }
  
}
