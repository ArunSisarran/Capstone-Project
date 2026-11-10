import React from 'react'
import {Outlet, Navigate} from 'react-router-dom';
import {useAuth} from '../context/AuthContext'


const ProtectedRoute = () => {
    const {user, isLoggedIn, loading} = useAuth();

    if (loading) return <p>Loading...</p>;

    return isLoggedIn? <Outlet /> : <Navigate to = "/login" />;
};

export default ProtectedRoute;