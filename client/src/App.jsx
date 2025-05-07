import React from 'react'
import {BrowserRouter,Routes,Route} from 'react-router-dom'
import Landpg from './pages/Landpg'
import Home from './pages/Home'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import Header from './components/Header'

export default function App() {
  return (
    <BrowserRouter>
    <Header/>
    <Routes>
      <Route path="/" element={<Landpg/>}></Route>
      <Route path="/" element={<Home/>}></Route>
      <Route path="/" element={<SignIn/>}></Route>
      <Route path="/" element={<SignUp/>}></Route>
    </Routes>
    </BrowserRouter>
  )
}
