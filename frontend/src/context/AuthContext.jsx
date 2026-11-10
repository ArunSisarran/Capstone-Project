import React, {createContext, useContext, useState, useEffect} from 'react';
import {base_url} from '../api/api.js'

const AuthContext  = createContext();

export const AuthProvider = ({children}) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState (null);
    const [loading, setLoading] = useState(true);
    const [isLoggedIn,setIsLoggedIn] = useState(false);


    const login  = (userData, accessToken) => {

        localStorage.setItem("token",accessToken);
  
        setUser(userData);
        setToken(accessToken);
        setIsLoggedIn(true);
    }

    const logout = () =>{
        localStorage.removeItem("token");

        setUser(null);
        setToken(null);
        setIsLoggedIn(false);


    }

    useEffect(() => {

        const checkAuth = async () =>{
           
                 console.log("1. useEffect started");


           const savedToken = localStorage.getItem("token");

               console.log("2. Saved token exists:", !!savedToken);

            if(!savedToken){
                setUser(null);
               setToken(null);
                setIsLoggedIn(false);
               setLoading(false);

               return;
           }

        try{
            console.log("3. Before fetch");

            const response = await fetch (
                `${base_url}/users/me`,
                {
                method : "GET",
                headers:{
                    //"Content-Type":"application/json",
                    Authorization: `Bearer ${savedToken}`
                },
            });
               console.log("4. Fetch completed");

                console.log("5. Status:", response.status);


            const data = await response.json();
             console.log("6. User Data:", data);


            if(!response.ok){
                throw new Error(data.message || "Authentication failed!");
            }

            
            setUser(data);
            setToken(savedToken);
            setIsLoggedIn(true);
  
      } catch (error){
        
        console.error("Auth Error:", error);

        localStorage.removeItem("token");

        setUser(null);
        setToken(null);
        setIsLoggedIn(false);

      } finally{
        setLoading(false);
      }

        };

        checkAuth();
    },[])

    return (
        <AuthContext.Provider
            value = {{
                user,
                token,
                isLoggedIn,
                loading,
                login,
                logout
            }}
        >
        {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
