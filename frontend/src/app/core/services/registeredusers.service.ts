import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AuthService } from './auth.service';
import { catchError, Observable, throwError } from 'rxjs';
import { TokenPayload } from '../interfaces/user.interface';

@Injectable({
  providedIn: 'root'
})
export class RegisteredusersService {
  private baseUrl = "http://localhost:8000/api/admin";
  constructor(private http: HttpClient, private authService: AuthService) { }

  private getHeaders():HttpHeaders{
    const token = this.authService.getToken();
    if(!token){
      throw new Error("No Token Available. Please Log In")
    }
    return new HttpHeaders().set('Authorization',`Bearer ${token}`)
  }

  getAllRegistered():Observable<TokenPayload[]> {
    return this.http.get<TokenPayload[]>(`${this.baseUrl}/getallregistereduseradmin`, {headers: this.getHeaders()}).pipe(
      catchError(error => {
        console.error("Error Fetching Users",error)
        return throwError(()=>({ message: error.error?.detail || "Error fetching users", detail:error.error?.detail }))
      })
    );
  }

}


