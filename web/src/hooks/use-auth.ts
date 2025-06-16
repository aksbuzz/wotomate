import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { useState } from 'react';
import {
  getApiAuthMeOptions,
  getApiAuthMeQueryKey,
  postApiAuthLoginMutation,
  postApiAuthRegisterMutation,
} from '@/client/@tanstack/react-query.gen';

const isLoggedIn = () => localStorage.getItem('accessToken') !== null;

const useAuth = () => {
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: user } = useQuery({
    ...getApiAuthMeOptions({
      headers: {
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
      },
    }),
    enabled: isLoggedIn(),
  });

  const registerUserMutation = useMutation({
    ...postApiAuthRegisterMutation({}),
    onSuccess: () => {
      navigate({ to: '/login' });
    },
    onError: error => {
      setError(error.err || 'Registration failed');
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: getApiAuthMeQueryKey({}) });
    },
  });

  const loginUserMutation = useMutation({
    ...postApiAuthLoginMutation({}),
    onSuccess: data => {
      localStorage.setItem('accessToken', data.access_token!);
      navigate({ to: '/' });
      queryClient.invalidateQueries({ queryKey: getApiAuthMeQueryKey({}) });
      setError(null);
    },
    onError: error => {
      setError(error.err || 'Login failed');
    },
  });

  const logoutUser = () => {
    localStorage.removeItem('accessToken');
    queryClient.invalidateQueries({ queryKey: getApiAuthMeQueryKey({}) });
    navigate({ to: '/login' });
  };

  return {
    user,
    error,
    registerUserMutation,
    loginUserMutation,
    logoutUser,
    resetError: () => setError(null),
  };
};

export { isLoggedIn };
export default useAuth;
