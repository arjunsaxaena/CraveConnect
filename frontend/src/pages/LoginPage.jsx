import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../context/AuthContext';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';

const LoginPage = () => {
  const [loginMethod, setLoginMethod] = useState('phone'); // 'phone' or 'google'
  const [verificationSent, setVerificationSent] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState(null);

  // Phone login form
  const phoneLoginForm = useFormik({
    initialValues: {
      phone: '',
      verificationCode: '',
    },
    validationSchema: Yup.object({
      phone: Yup.string()
        .required('Phone number is required')
        .matches(/^[0-9]{10}$/, 'Phone number must be 10 digits'),
      verificationCode: verificationSent
        ? Yup.string()
            .required('Verification code is required')
            .matches(/^[0-9]{6}$/, 'Verification code must be 6 digits')
        : Yup.string(),
    }),
    onSubmit: async (values) => {
      try {
        setError(null);
        
        if (!verificationSent) {
          // Send verification code
          // In a real app, this would call AuthService.sendVerificationCode(values.phone)
          console.log('Sending verification code to:', values.phone);
          setVerificationSent(true);
        } else {
          // Verify code and login
          // In a real app, this would call AuthService.verifyPhone(values.phone, values.verificationCode)
          // followed by login with the returned token
          await login({
            phone: values.phone,
            verification_code: values.verificationCode,
          });
          navigate('/');
        }
      } catch (err) {
        console.error('Login error:', err);
        setError(err.response?.data?.message || 'Login failed. Please try again.');
      }
    },
  });

  // Handle Google login
  const handleGoogleLogin = () => {
    // In a real app, this would redirect to the Google OAuth flow
    console.log('Logging in with Google');
    // Once auth is complete, the user would be redirected back to the app
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Sign In</h1>
          <p className="mt-2 text-sm text-gray-600">
            Welcome back! Sign in to access your account
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}

        {/* Login method tabs */}
        <div className="flex border-b border-gray-200 mb-6">
          <button
            className={`pb-2 px-4 text-sm font-medium ${
              loginMethod === 'phone'
                ? 'border-b-2 border-primary-600 text-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setLoginMethod('phone')}
          >
            Phone Number
          </button>
          <button
            className={`pb-2 px-4 text-sm font-medium ${
              loginMethod === 'google'
                ? 'border-b-2 border-primary-600 text-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setLoginMethod('google')}
          >
            Google
          </button>
        </div>

        {/* Phone login form */}
        {loginMethod === 'phone' && (
          <form onSubmit={phoneLoginForm.handleSubmit}>
            <Input
              label="Phone Number"
              id="phone"
              name="phone"
              type="tel"
              placeholder="Enter your phone number"
              value={phoneLoginForm.values.phone}
              onChange={phoneLoginForm.handleChange}
              onBlur={phoneLoginForm.handleBlur}
              error={phoneLoginForm.touched.phone && phoneLoginForm.errors.phone}
              touched={phoneLoginForm.touched.phone}
              required
            />

            {verificationSent && (
              <Input
                label="Verification Code"
                id="verificationCode"
                name="verificationCode"
                type="text"
                placeholder="Enter 6-digit code"
                value={phoneLoginForm.values.verificationCode}
                onChange={phoneLoginForm.handleChange}
                onBlur={phoneLoginForm.handleBlur}
                error={
                  phoneLoginForm.touched.verificationCode &&
                  phoneLoginForm.errors.verificationCode
                }
                touched={phoneLoginForm.touched.verificationCode}
                required
              />
            )}

            <Button
              type="submit"
              className="w-full mt-4"
              isLoading={phoneLoginForm.isSubmitting}
            >
              {verificationSent ? 'Verify & Sign In' : 'Send Verification Code'}
            </Button>
          </form>
        )}

        {/* Google login */}
        {loginMethod === 'google' && (
          <div className="mt-2">
            <button
              type="button"
              className="w-full flex items-center justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
              onClick={handleGoogleLogin}
            >
              <svg
                className="w-5 h-5 mr-2"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
              >
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
                <path fill="none" d="M1 1h22v22H1z" />
              </svg>
              Sign in with Google
            </button>
          </div>
        )}

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-600 hover:text-primary-700 font-medium">
              Sign up
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;
