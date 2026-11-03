import { useState } from 'react'
import './App.css'
import {BrowserRouter, Routes,Route} from 'react-router-dom'
import HomePage from './pages/HomePage'
import ResultPage from './pages/ResultPage'
import ResultDetailsPage from './pages/ResultDetailsPage'
import Signup from './pages/SignupForm'
import Login from './pages/LoginForm'
import Profile from './pages/Profile'
import Navbar from './components/Navbar'

function App() {
  return(
    <>
    <BrowserRouter>
      <Navbar />

      <Routes>
          <Route path="/" element = {<HomePage />} />
          <Route path="/result" element = {<ResultPage />} />
          <Route path="/result/:id" element={<ResultDetailsPage />} />
          <Route path="/login" element = {<Login />} />
          <Route path="/signup" element = {<Signup />} />
          <Route path="/profile" element = {<Profile />} />                                       
      </Routes>
    </BrowserRouter>
    </>
  );
}

export default App;
