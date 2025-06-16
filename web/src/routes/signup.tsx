import { useState, type FormEvent } from 'react';
import useAuth, { isLoggedIn } from '@/hooks/use-auth';
import { createFileRoute, redirect, Link } from '@tanstack/react-router';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export const Route = createFileRoute('/signup')({
  component: SignUp,
  beforeLoad: () => {
    if (isLoggedIn()) {
      throw redirect({
        to: '/',
      });
    }
  },
});

function SignUp() {
  const { error, resetError, registerUserMutation } = useAuth();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    resetError();

    if (!email || !password) {
      console.error('Email and password are required');
      return;
    }

    registerUserMutation.mutateAsync({ body: { email, password } });
  };

  return (
    <div className={cn('flex flex-col gap-6 items-center justify-center min-h-screen p-4')}>
      {' '}
      {/* Added centering and padding */}
      <Card className="w-full max-w-md">
        {' '}
        {/* Added max-width for better appearance */}
        <CardHeader>
          <CardTitle>Create your account</CardTitle>
          <CardDescription>Enter your email and password below to signup.</CardDescription>{' '}
          {/* Slightly updated description */}
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div className="flex flex-col gap-6">
              <div className="grid gap-3">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  required
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  disabled={registerUserMutation.isPending}
                />
              </div>
              <div className="grid gap-3">
                <div className="flex items-center">
                  <Label htmlFor="password">Password</Label>
                  {/*
                  <Link // Using TanStack Router Link for internal navigation
                    to="/forgot-password" // Example route
                    className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                  >
                    Forgot your password?
                  </Link>
                  */}
                </div>
                <Input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  disabled={registerUserMutation.isPending}
                />
              </div>

              {error && (
                <p className="text-sm text-red-600 dark:text-red-500">
                  {/* Assuming error is an object with a message property or a string */}
                  {typeof error === 'string'
                    ? error
                    : (error as any)?.message || 'An unexpected error occurred.'}
                </p>
              )}

              <div className="flex flex-col gap-3">
                <Button type="submit" className="w-full" disabled={registerUserMutation.isPending}>
                  {registerUserMutation.isPending ? 'Signing up...' : 'Sign up'}
                </Button>
                {/*
                <Button variant="outline" className="w-full" disabled={loginUserMutation.isPending}>
                  Login with Google
                </Button>
                */}
              </div>
            </div>
            <div className="mt-4 text-center text-sm">
              Already have an account?{' '}
              <Link to="/login" className="underline underline-offset-4 hover:text-primary">
                Login
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
