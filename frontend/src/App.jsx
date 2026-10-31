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
  ///Uses Prop; Profile Page and ResultCard both needs store state
  const [history, setHistory] = useState([]);
  const [favorites,setFavorites] = useState([]);
  const [savedforlater, setSavedForLater] = useState([]);

  const [token,setToken] = useState(null);

  const [result,setResult] = useState([]);
  const [dataIsLoaded,setDataIsLoaded] = useState(false);

  return(
    <>
    <BrowserRouter>
      <Navbar 
        token={token}
      />

      <Routes>
          <Route path="/" element = {<HomePage />} />

          <Route path="/result" 
                 element = {<ResultPage
                            history={history}
                            setHistory={setHistory} 
                            favorites={favorites}
                            setFavorites={setFavorites}
                            savedforlater = {savedforlater}
                            setSavedForLater = {setSavedForLater}
                            result = {result}
                            setResult = {setResult}
                            />} 
                
          />

          <Route path="/result/:id" element={<ResultDetailsPage result = {result}/>} />

          <Route path="/login" element = {<Login token={token} setToken={setToken}/>} />

          <Route path="/signup" element = {<Signup />} />

          <Route path="/profile" 
                 element = {<Profile
                            history={history} 
                            setHistory={setHistory}
                            favorites={favorites}
                            setFavorites={setFavorites}
                            savedforlater = {savedforlater}
                            setSavedForLater = {setSavedForLater}
                            />} 
            />                                       
      </Routes>
    </BrowserRouter>
    </>
  );
}

export default App;
