import React, { useState } from "react"
import PasswordInput from "../../components/Input/PasswordInput"
import { Link, useNavigate } from "react-router-dom"
import { validateEmail } from "../../utils/helper"
import { useDispatch } from "react-redux"
import {
  signInFailure,
  signInStart,
  signInSuccess,
} from "../../redux/user/userSlice"
import axios from "axios"
import { toast } from "react-toastify"

const Login = () => {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const dispatch = useDispatch()
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault();
  
    // Basic validation
    if (!validateEmail(email)) {
      setError("Please enter a valid email address");
      return;
    }
  
    if (!password) {
      setError("Please enter the password");
      return;
    }
  
    setError("");
  
    // Login API call
    try {
      dispatch(signInStart());
  
      const res = await axios.post(
        "http://127.0.0.1:8000/signin",
        { email, password }
        // Optionally, you can use { withCredentials: true } for cookie handling
      );
      
      if (res.data.success === false) {
        console.log(res)
        toast.error(res.detail);
        console.log(res.data);
        dispatch(signInFailure(res.detail));
        return;
      }
  
      // Store the JWT token in localStorage
      const token = res.data.token;  // Assuming the token is returned in the response
      if (token) {
        localStorage.setItem("access_token", token);  // Store the JWT token in localStorage
        console.log("Token stored in localStorage:", token);
      }
  
      // Success handling
      toast.success(res.data.message);
      dispatch(signInSuccess(res.data));
  
      // Navigate to the home page or any other page
      navigate("/");
    } catch (error) {
      console.log(error.response.data.detail)
      toast.error(error.response.data.detail);
      dispatch(signInFailure(error.response.data.detail));
    }
  };
  
  return (
    <div className="flex items-center justify-center mt-28">
      <div className="w-96 border rounded bg-white px-7 py-10">
        <form onSubmit={handleLogin}>
          <h4 className="text-2xl mb-7">Login</h4>

          <input
            type="text"
            placeholder="Email"
            className="input-box"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <PasswordInput
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <p className="text-red-500 text-sm pb-1">{error}</p>}

          <button type="submit" className="btn-primary">
            LOGIN
          </button>

          <p className="text-sm text-center mt-4">
            Not registered yet?{" "}
            <Link
              to={"/signup"}
              className="font-medium text-[#2B85FF] underline"
            >
              Create an account
            </Link>
          </p>
        </form>
      </div>
    </div>
  )
}

export default Login
