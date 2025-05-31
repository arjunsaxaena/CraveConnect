import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../context/AuthContext';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';

const RegisterPage = () => {
  const [registerMethod, setRegisterMethod] = useState('phone'); // 'phone' or 'google'
  const [verificationSent, setVerificationSent] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState(null);

  // Phone registration form
  const phoneRegisterForm = useFormik({
    initialValues: {
      name: '',
      phone: '',
      verificationCode: '',
    },
    validationSchema: Yup.object({
      name: Yup.string().required('Name is required'),
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
          // Verify code and register
          // In a real app, this would call AuthService.register with all user data
          await register({
            name: values.name,
            phone: values.phone,
            verification_code: values.verificationCode,
            auth_provider: 'phone',
          });
          navigate('/');
        }
      } catch (err) {
        console.error('Registration error:', err);
        setError(err.response?.data?.message || 'Registration failed. Please try again.');
      }
    },
  });

  // Handle Google registration
  const handleGoogleRegister = () => {
    // In a real app, this would redirect to the Google OAuth flow
    console.log('Registering with Google');
    // Once auth is complete, the user would be redirected back to the app
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <Card className="w-full max-w-md p-8">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Create Account</h1>
          <p className="mt-2 text-sm text-gray-600">
            Join CraveConnect to discover great food experiences
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">
            {error}
          </div>
        )}

        {/* Registration method tabs */}
        <div className="flex border-b border-gray-200 mb-6">
          <button
            className={`pb-2 px-4 text-sm font-medium ${
              registerMethod === 'phone'
                ? 'border-b-2 border-primary-600 text-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setRegisterMethod('phone')}
          >
            Phone Number
          </button>
          <button
            className={`pb-2 px-4 text-sm font-medium ${
              registerMethod === 'google'
                ? 'border-b-2 border-primary-600 text-primary-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setRegisterMethod('google')}
          >
            Google
          </button>
        </div>

        {/* Phone registration form */}
        {registerMethod === 'phone' && (
          <form onSubmit={phoneRegisterForm.handleSubmit}>
            <Input
              label="Full Name"
              id="name"
              name="name"
              type="text"
              placeholder="Enter your full name"
              value={phoneRegisterForm.values.name}
              onChange={phoneRegisterForm.handleChange}
              onBlur={phoneRegisterForm.handleBlur}
              error={phoneRegisterForm.touched.name && phoneRegisterForm.errors.name}
              touched={phoneRegisterForm.touched.name}
              required
            />

            <Input
              label="Phone Number"
              id="phone"
              name="phone"
              type="tel"
              placeholder="Enter your phone number"
              value={phoneRegisterForm.values.phone}
              onChange={phoneRegisterForm.handleChange}
              onBlur={phoneRegisterForm.handleBlur}
              error={phoneRegisterForm.touched.phone && phoneRegisterForm.errors.phone}
              touched={phoneRegisterForm.touched.phone}
              required
            />

            {verificationSent && (
              <Input
                label="Verification Code"
                id="verificationCode"
                name="verificationCode"
                type="text"
                placeholder="Enter 6-digit code"
                value={phoneRegisterForm.values.verificationCode}
                onChange={phoneRegisterForm.handleChange}
                onBlur={phoneRegisterForm.handleBlur}
                error={
                  phoneRegisterForm.touched.verificationCode &&
                  phoneRegisterForm.errors.verificationCode
                }
                touched={phoneRegisterForm.touched.verificationCode}
                required
              />
            )}

            <Button
              type="submit"
              className="w-full mt-4"
              isLoading={phoneRegisterForm.isSubmitting}
            >
              {verificationSent ? 'Verify & Create Account' : 'Send Verification Code'}
            </Button>
          </form>
        )}

        {/* Google registration */}
        {registerMethod === 'google' && (
          <div className="mt-2">
            <button
              type="button"
              className="w-full flex items-center justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
              onClick={handleGoogleRegister}
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
              Sign up with Google
            </button>
          </div>
        )}

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
              Sign in
            </Link>
          </p>
        </div>

        <div className="mt-6 text-xs text-center text-gray-500">
          By creating an account, you agree to our{' '}
          <Link to="/terms" className="text-primary-600 hover:text-primary-700">
            Terms of Service
          </Link>{' '}
          and{' '}
          <Link to="/privacy" className="text-primary-600 hover:text-primary-700">
            Privacy Policy
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default RegisterPage;
