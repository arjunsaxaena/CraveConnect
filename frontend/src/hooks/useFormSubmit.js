import { useState } from 'react';
import { useFormik } from 'formik';

/**
 * A custom hook for handling form submission with API calls
 * 
 * @param {Object} options - The options object
 * @param {Object} options.initialValues - Initial form values
 * @param {Object} options.validationSchema - Yup validation schema
 * @param {Function} options.onSubmit - Form submit handler function
 * @param {Function} options.apiCall - API function to call
 * @returns {Object} - The formik object and additional state properties
 */
const useFormSubmit = ({ initialValues, validationSchema, onSubmit, apiCall }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const formik = useFormik({
    initialValues,
    validationSchema,
    onSubmit: async (values, { resetForm }) => {
      try {
        setIsSubmitting(true);
        setSubmitError(null);
        setSubmitSuccess(false);
        
        // If apiCall is provided, call it with form values
        if (apiCall) {
          await apiCall(values);
        }
        
        // If onSubmit is provided, call it with form values
        if (onSubmit) {
          await onSubmit(values);
        }
        
        setSubmitSuccess(true);
        
        // Reset the form if the submission is successful
        resetForm();
      } catch (error) {
        setSubmitError(error.message || 'An error occurred during submission');
      } finally {
        setIsSubmitting(false);
      }
    },
  });

  return {
    formik,
    isSubmitting,
    submitError,
    submitSuccess,
    setSubmitError,
    setSubmitSuccess,
  };
};

export default useFormSubmit;
