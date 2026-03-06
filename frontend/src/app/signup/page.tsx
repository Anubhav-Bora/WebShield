'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { register } from '@/services/auth'
import { useNotificationStore } from '@/store/useNotificationStore'
import { UserPlus, Mail, Lock, User } from 'lucide-react'

export default function SignupPage() {
    const router = useRouter()
    const { success, error } = useNotificationStore()
    const [isLoading, setIsLoading] = useState(false)
    const [passwordStrength, setPasswordStrength] = useState(0)
    const [formData, setFormData] = useState({
        email: '',
        username: '',
        full_name: '',
        password: '',
        confirmPassword: ''
    })
    const [errors, setErrors] = useState<Record<string, string>>({})

    const validatePasswordStrength = (password: string) => {
        let strength = 0
        if (password.length >= 12) strength++
        if (/[A-Z]/.test(password)) strength++
        if (/[a-z]/.test(password)) strength++
        if (/\d/.test(password)) strength++
        if (/[!@#$%^&*()_+\-=\[\]{};:'"",.<>?/\\|`~]/.test(password)) strength++
        setPasswordStrength(strength)
        return strength
    }

    const getPasswordStrengthColor = () => {
        if (passwordStrength === 0) return 'bg-slate-600'
        if (passwordStrength <= 2) return 'bg-red-500'
        if (passwordStrength <= 3) return 'bg-yellow-500'
        if (passwordStrength <= 4) return 'bg-blue-500'
        return 'bg-green-500'
    }

    const getPasswordStrengthText = () => {
        if (passwordStrength === 0) return 'No password'
        if (passwordStrength <= 2) return 'Weak'
        if (passwordStrength <= 3) return 'Fair'
        if (passwordStrength <= 4) return 'Good'
        return 'Strong'
    }

    const validateForm = () => {
        const newErrors: Record<string, string> = {}

        if (!formData.email) newErrors.email = 'Email is required'
        if (!formData.username) newErrors.username = 'Username is required'
        if (formData.username.length < 3) newErrors.username = 'Username must be at least 3 characters'
        if (!/^[a-zA-Z0-9_-]+$/.test(formData.username)) {
            newErrors.username = 'Username can only contain letters, numbers, underscores, and hyphens'
        }
        if (!formData.full_name) newErrors.full_name = 'Full name is required'
        if (!formData.password) newErrors.password = 'Password is required'
        if (formData.password.length < 12) newErrors.password = 'Password must be at least 12 characters'
        if (!/[A-Z]/.test(formData.password)) newErrors.password = 'Password must contain uppercase letter'
        if (!/[a-z]/.test(formData.password)) newErrors.password = 'Password must contain lowercase letter'
        if (!/\d/.test(formData.password)) newErrors.password = 'Password must contain a digit'
        if (!/[!@#$%^&*()_+\-=\[\]{};:'"",.<>?/\\|`~]/.test(formData.password)) {
            newErrors.password = 'Password must contain a special character'
        }
        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match'
        }

        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!validateForm()) {
            return
        }

        setIsLoading(true)

        try {
            await register({
                email: formData.email,
                username: formData.username,
                full_name: formData.full_name,
                password: formData.password
            })

            success('Account created!', 'Your account has been created successfully. Please log in.')
            router.push('/login')
        } catch (err: any) {
            error('Signup failed', err.detail || 'Failed to create account')
        } finally {
            setIsLoading(false)
        }
    }

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const password = e.target.value
        setFormData({ ...formData, password })
        validatePasswordStrength(password)
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                <div className="glass rounded-2xl border border-slate-700/50 p-8 shadow-2xl">
                    <div className="text-center mb-8">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-indigo-500/20 border-2 border-indigo-500/30 mb-4">
                            <UserPlus className="w-8 h-8 text-indigo-400" />
                        </div>
                        <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
                        <p className="text-slate-400">Join WebShield and manage your webhooks</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">
                                Email
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="email"
                                    id="email"
                                    value={formData.email}
                                    onChange={(e) => {
                                        setFormData({ ...formData, email: e.target.value })
                                        if (errors.email) setErrors({ ...errors, email: '' })
                                    }}
                                    className={`w-full pl-10 pr-4 py-3 bg-slate-800/50 border rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-colors ${errors.email ? 'border-red-500' : 'border-slate-600 focus:border-indigo-500'
                                        }`}
                                    placeholder="your@email.com"
                                />
                            </div>
                            {errors.email && <p className="text-red-400 text-xs mt-1">{errors.email}</p>}
                        </div>

                        <div>
                            <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-2">
                                Username
                            </label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="text"
                                    id="username"
                                    value={formData.username}
                                    onChange={(e) => {
                                        setFormData({ ...formData, username: e.target.value })
                                        if (errors.username) setErrors({ ...errors, username: '' })
                                    }}
                                    className={`w-full pl-10 pr-4 py-3 bg-slate-800/50 border rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-colors ${errors.username ? 'border-red-500' : 'border-slate-600 focus:border-indigo-500'
                                        }`}
                                    placeholder="username"
                                />
                            </div>
                            {errors.username && <p className="text-red-400 text-xs mt-1">{errors.username}</p>}
                        </div>

                        <div>
                            <label htmlFor="full_name" className="block text-sm font-medium text-slate-300 mb-2">
                                Full Name
                            </label>
                            <input
                                type="text"
                                id="full_name"
                                value={formData.full_name}
                                onChange={(e) => {
                                    setFormData({ ...formData, full_name: e.target.value })
                                    if (errors.full_name) setErrors({ ...errors, full_name: '' })
                                }}
                                className={`w-full px-4 py-3 bg-slate-800/50 border rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-colors ${errors.full_name ? 'border-red-500' : 'border-slate-600 focus:border-indigo-500'
                                    }`}
                                placeholder="John Doe"
                            />
                            {errors.full_name && <p className="text-red-400 text-xs mt-1">{errors.full_name}</p>}
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="password"
                                    id="password"
                                    value={formData.password}
                                    onChange={handlePasswordChange}
                                    className={`w-full pl-10 pr-4 py-3 bg-slate-800/50 border rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-colors ${errors.password ? 'border-red-500' : 'border-slate-600 focus:border-indigo-500'
                                        }`}
                                    placeholder="Enter password"
                                />
                            </div>
                            {formData.password && (
                                <div className="mt-2">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-xs text-slate-400">Strength:</span>
                                        <span className={`text-xs font-semibold ${passwordStrength <= 2 ? 'text-red-400' :
                                            passwordStrength <= 3 ? 'text-yellow-400' :
                                                passwordStrength <= 4 ? 'text-blue-400' :
                                                    'text-green-400'
                                            }`}>
                                            {getPasswordStrengthText()}
                                        </span>
                                    </div>
                                    <div className="w-full bg-slate-700 rounded-full h-1.5">
                                        <div
                                            className={`h-1.5 rounded-full transition-all ${getPasswordStrengthColor()}`}
                                            style={{ width: `${(passwordStrength / 5) * 100}%` }}
                                        />
                                    </div>
                                    <div className="mt-2 text-xs text-slate-400 space-y-1">
                                        <div className={/[A-Z]/.test(formData.password) ? 'text-green-400' : ''}>
                                            ✓ Uppercase letter
                                        </div>
                                        <div className={/[a-z]/.test(formData.password) ? 'text-green-400' : ''}>
                                            ✓ Lowercase letter
                                        </div>
                                        <div className={/\d/.test(formData.password) ? 'text-green-400' : ''}>
                                            ✓ Number
                                        </div>
                                        <div className={/[!@#$%^&*()_+\-=\[\]{};:'"",.<>?/\\|`~]/.test(formData.password) ? 'text-green-400' : ''}>
                                            ✓ Special character
                                        </div>
                                        <div className={formData.password.length >= 12 ? 'text-green-400' : ''}>
                                            ✓ At least 12 characters
                                        </div>
                                    </div>
                                </div>
                            )}
                            {errors.password && <p className="text-red-400 text-xs mt-1">{errors.password}</p>}
                        </div>

                        <div>
                            <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-300 mb-2">
                                Confirm Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                                <input
                                    type="password"
                                    id="confirmPassword"
                                    value={formData.confirmPassword}
                                    onChange={(e) => {
                                        setFormData({ ...formData, confirmPassword: e.target.value })
                                        if (errors.confirmPassword) setErrors({ ...errors, confirmPassword: '' })
                                    }}
                                    className={`w-full pl-10 pr-4 py-3 bg-slate-800/50 border rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-colors ${errors.confirmPassword ? 'border-red-500' : 'border-slate-600 focus:border-indigo-500'
                                        }`}
                                    placeholder="Confirm password"
                                />
                            </div>
                            {errors.confirmPassword && <p className="text-red-400 text-xs mt-1">{errors.confirmPassword}</p>}
                        </div>

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/30 mt-6"
                        >
                            {isLoading ? 'Creating account...' : 'Create Account'}
                        </button>
                    </form>

                    <div className="mt-6 text-center text-sm text-slate-400">
                        Already have an account?{' '}
                        <Link href="/login" className="text-indigo-400 hover:text-indigo-300 font-semibold transition-colors">
                            Sign in
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}
