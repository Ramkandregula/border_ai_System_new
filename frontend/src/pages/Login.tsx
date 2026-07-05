import React from 'react';
import { useForm } from 'react-hook-form';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import toast from 'react-hot-toast';
import { Lock, Mail } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [loading, setLoading] = React.useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data: any) => {
    try {
      setLoading(true);
      const response = await authService.login(data.username, data.password);
      setAuth(response.user, response.access_token);
      toast.success('Login successful!');
      navigate('/');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-400 to-cyan-400 flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">🛡️</span>
          </div>
          <h1 className="text-4xl font-bold gradient-text">Border AI</h1>
          <p className="text-gray-400 mt-2">Control System</p>
        </div>

        {/* Login Form */}
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="glass p-8 rounded-xl space-y-6 border border-white/10"
        >
          <div>
            <label className="block text-sm font-semibold mb-2">Username</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="text"
                {...register('username', { required: 'Username is required' })}
                className="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:border-blue-400 transition-colors"
                placeholder="Enter your username"
              />
            </div>
            {errors.username && <p className="text-red-400 text-sm mt-1">{String(errors.username.message)}</p>}
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
              <input
                type="password"
                {...register('password', { required: 'Password is required' })}
                className="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:border-blue-400 transition-colors"
                placeholder="Enter your password"
              />
            </div>
            {errors.password && <p className="text-red-400 text-sm mt-1">{String(errors.password.message)}</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 py-2 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin">⏳</span> Logging in...
              </>
            ) : (
              'Login'
            )}
          </button>
        </form>

        {/* Demo Credentials */}
        <div className="mt-6 glass p-4 rounded-xl border border-white/10">
          <p className="text-sm text-gray-400 mb-2">Demo Credentials:</p>
          <p className="text-sm font-mono">Username: <span className="text-blue-400">admin</span></p>
          <p className="text-sm font-mono">Password: <span className="text-blue-400">password123</span></p>
        </div>
      </div>
    </div>
  );
};

export default Login;
