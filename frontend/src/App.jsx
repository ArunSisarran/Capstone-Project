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
import FavoritePage from './components/FavoritePage'
import SavedForLaterPage from './components/SavedForLaterPage' 

function App() {
  ///Uses Prop to store states
  const [history, setHistory] = useState([]);
  const [favorites,setFavorites] = useState([]);
  const [savedforlater, setSavedForLater] = useState([]);

  const [result,setResult] = useState([]);

  const [token,setToken] = useState(null);

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

          <Route path="/login" element = {<Login 
                                            token={token} 
                                            setToken={setToken}/
                                          >} />

          <Route path="/signup" element = {<Signup />} />

          <Route path="/profile" 
                 element = {<Profile
                            history={history} 
                            setHistory={setHistory}
                            favorites={favorites}
                            setFavorites={setFavorites}
                            savedforlater = {savedforlater}
                            setSavedForLater = {setSavedForLater}
                            token = {token}
                            setToken = {setToken}
                            />} 
            />     

          <Route path = "/favorite"
                 element = {<FavoritePage 
                            history={history} 
                            setHistory={setHistory}
                            favorites = {favorites} 
                            setFavorites = {setFavorites} 
                            savedforlater = {savedforlater} 
                            setSavedForLater = {setSavedForLater}
                            token={token} 
                            setToken={setToken}
                            />} 
            />

            <Route path = "/savedforlater" 
                  element ={<SavedForLaterPage 
                            favorites = {favorites} 
                            setFavorites = {setFavorites} 
                            savedforlater = {savedforlater} 
                            setSavedForLater = {setSavedForLater} 
                            token={token} 
                            setToken={setToken}
                            />}  
              />

      </Routes>
    </BrowserRouter>
    </>
  );
}

export default App;
