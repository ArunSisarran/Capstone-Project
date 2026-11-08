import React, {createContext, useContext, useState} from 'react';

const AuthContext  = createContext();

export const AuthProvider = ({children}) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState (null);
    const [loading, setLoading] = useState(true);
    const [isLoggedIn,setIsLoggedIn] = useState(false);

    const login  = (userData, accessToken) => {

        setUser(userData);
        setToken(accessToken);
        setIsLoggedIn(true);
    }

    const logout = () =>{

        setUser(null);
        setToken(null);
        setIsLoggedIn(false);
    }

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
