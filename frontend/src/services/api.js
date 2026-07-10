/**
 * CAMADA DE SERVIÇOS DE API (api.js)
 * 
 * Este arquivo centraliza todas as comunicações com o backend FastAPI.
 * Foi escrito de forma didática para explicar como o React se comunica com a API REST.
 */

// Define a URL base do backend.
// Se houver uma variável de ambiente VITE_API_URL (ex: na hospedagem de produção), ela será usada.
// Caso contrário, por padrão, aponta para o servidor FastAPI rodando localmente na porta 8000.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Função para decodificar um Token JWT no frontend.
 * Um token JWT é composto por 3 partes separadas por pontos: Header.Payload.Signature
 * O Payload é apenas uma string em Base64 contendo os dados do token (como o e-mail no campo 'sub').
 * Podemos ler essa string sem precisar da assinatura secreta (que só o backend possui para validar).
 */
export function decodeTokenPayload(token) {
  try {
    const payloadBase64 = token.split('.')[1];
    // Decodifica a string Base64 e lida com caracteres especiais (UTF-8)
    const jsonString = atob(payloadBase64.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(jsonString);
  } catch (error) {
    console.error('Erro ao decodificar o token JWT:', error);
    return null;
  }
}

/**
 * 1. EFETUAR LOGIN (POST /auth/token)
 * 
 * ATENÇÃO DIDÁTICA:
 * O seu backend FastAPI utiliza a dependência OAuth2PasswordRequestForm.
 * Isso significa que ele NÃO espera um JSON no corpo da requisição, mas sim
 * um formulário codificado em URL (application/x-www-form-urlencoded).
 * Além disso, o formulário exige o campo 'username' para o e-mail, e 'password' para a senha.
 */
export async function login(email, password) {
  const url = `${API_BASE_URL}/auth/token`;

  // Construímos os parâmetros no formato de formulário (URL-encoded)
  const bodyParams = new URLSearchParams();
  bodyParams.append('username', email); // FastAPI espera 'username'
  bodyParams.append('password', password);

  console.log(`[API] Enviando requisição de Login para: ${url}`);

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: bodyParams.toString(),
  });

  if (!response.ok) {
    // Caso ocorra algum erro (401, 404, etc), tentamos ler a mensagem do backend
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao efetuar login.';
    throw new Error(message);
  }

  // Em caso de sucesso, o backend retorna: { access_token: "...", token_type: "Bearer" }
  return await response.json();
}

/**
 * 2. CRIAR CONTA DE USUÁRIO (POST /users/)
 * 
 * Diferente do login, a rota de criação de usuários no seu backend
 * espera um JSON (definido pelo seu UserSchema do Pydantic).
 */
export async function registerUser({ first_name, last_name, email, password }) {
  const url = `${API_BASE_URL}/users/`;

  const bodyData = {
    first_name: first_name,
    last_name: last_name,
    email: email,
    password: password
  };

  console.log(`[API] Enviando dados de cadastro para: ${url}`, { ...bodyData, password: '***' });

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(bodyData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao criar conta.';
    throw new Error(message);
  }

  // O backend retorna os dados públicos do usuário criado (UserPublic)
  return await response.json();
}

/**
 * 2b. CRIAR CONTA DE PROFISSIONAL (POST /users/professional) - Apenas Admin
 */
export async function createProfessional({ first_name, last_name, email, password }, token) {
  const url = `${API_BASE_URL}/users/professional`;

  const bodyData = {
    first_name,
    last_name,
    email,
    password
  };

  console.log(`[API] Criando profissional em: ${url}`, { ...bodyData, password: '***' });

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(bodyData)
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao criar profissional.';
    throw new Error(message);
  }

  return await response.json();
}


/**
 * 3. BUSCAR TODOS OS USUÁRIOS (GET /users/)
 * 
 * Usamos esta rota para listar usuários. Não exige permissão no backend,
 * mas utilizaremos para encontrar os detalhes do usuário logado através do e-mail.
 */
export async function fetchUsers(token) {
  const url = `${API_BASE_URL}/users/?offset=0&limit=100`;

  console.log(`[API] Buscando lista de usuários de: ${url}`);

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao obter lista de usuários.';
    throw new Error(message);
  }

  // Retorna { users: [...] }
  return await response.json();
}

/**
 * 4. BUSCAR PERFIL DO USUÁRIO LOGADO
 * 
 * Agora integrando com a rota segura GET /users/me do backend.
 */
export async function fetchLoggedInUserProfile(token) {
  const url = `${API_BASE_URL}/users/me`;

  console.log(`[API] Buscando perfil do usuário logado de: ${url}`);

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao obter perfil do usuário.';
    throw new Error(message);
  }

  return await response.json();
}

/**
 * 5. ATUALIZAR DADOS DO USUÁRIO (PUT /users/{id})
 */
export async function updateUser(userId, { first_name, last_name, email, password }, token) {
  const url = `${API_BASE_URL}/users/${userId}`;

  const bodyData = {
    first_name,
    last_name,
    email,
    password,
  };

  console.log(`[API] Atualizando usuário ${userId} em: ${url}`);

  const response = await fetch(url, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(bodyData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao atualizar dados.';
    throw new Error(message);
  }

  return await response.json();
}

/**
 * 6. DELETAR PERFIL DO USUÁRIO (DELETE /users/{id})
 */
export async function deleteUser(userId, token) {
  const url = `${API_BASE_URL}/users/${userId}`;

  console.log(`[API] Deletando usuário ${userId} em: ${url}`);

  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao deletar usuário.';
    throw new Error(message);
  }

  return await response.json();
}

/**
 * 7. BUSCAR TODOS OS SERVIÇOS (GET /services/)
 */
export async function fetchServices() {
  const url = `${API_BASE_URL}/services/`;

  console.log(`[API] Buscando lista de serviços de: ${url}`);

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao obter lista de serviços.';
    throw new Error(message);
  }

  // Retorna { services: [...] }
  return await response.json();
}

/**
 * 8. CRIAR NOVO SERVIÇO (POST /services/)
 */
export async function createService({ name, duration, price }, token) {
  const url = `${API_BASE_URL}/services/`;

  const bodyData = {
    name,
    duration: parseInt(duration),
    price: parseFloat(price),
  };

  console.log(`[API] Criando serviço em: ${url}`);

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(bodyData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao criar serviço.';
    throw new Error(message);
  }

  return await response.json();
}

/**
 * 9. ATUALIZAR SERVIÇO (PATCH /services/{id})
 */
export async function updateService(serviceId, serviceData, token) {
  const url = `${API_BASE_URL}/services/${serviceId}`;

  const bodyData = {};
  if (serviceData.name !== undefined) bodyData.name = serviceData.name;
  if (serviceData.duration !== undefined) bodyData.duration = parseInt(serviceData.duration);
  if (serviceData.price !== undefined) bodyData.price = parseFloat(serviceData.price);

  console.log(`[API] Atualizando serviço ${serviceId} em: ${url}`);

  const response = await fetch(url, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(bodyData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao atualizar serviço.';
    throw new Error(message);
  }

  return await response.json();
}

/**
 * 10. DELETAR SERVIÇO (DELETE /services/{id})
 */
export async function deleteService(serviceId, token) {
  const url = `${API_BASE_URL}/services/${serviceId}`;

  console.log(`[API] Deletando serviço ${serviceId} em: ${url}`);

  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao deletar serviço.';
    throw new Error(message);
  }

  return await response.json();
}

/**
 * 11. BUSCAR SELEÇÃO DE CLIENTES E PROFISSIONAIS PARA AGENDAMENTO (GET /appointments/selection)
 */
export async function fetchAppointmentsSelection(token) {
  const url = `${API_BASE_URL}/appointments/selection`;

  console.log(`[API] Buscando seleção de usuários em: ${url}`);

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao obter lista de seleção para agendamento.';
    throw new Error(message);
  }

  return await response.json();
}

/**
 * 12. BUSCAR GRADE DE HORÁRIOS / SLOTS DISPONÍVEIS (GET /appointments/slots)
 */
export async function fetchAppointmentSlots({ service_id, client_id, professional_id }, token) {
  const params = new URLSearchParams();
  if (service_id) params.append('service_id', service_id);
  if (client_id) params.append('client_id', client_id);
  if (professional_id) params.append('professional_id', professional_id);

  const url = `${API_BASE_URL}/appointments/slots?${params.toString()}`;

  console.log(`[API] Buscando slots de agendamento em: ${url}`);

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao obter slots de horário.';
    throw new Error(message);
  }

  return await response.json();
}

/**
 * 13. CRIAR NOVO AGENDAMENTO (POST /appointments/)
 */
export async function createAppointment({ client_id, professional_id, service_id, start_time }, token) {
  const url = `${API_BASE_URL}/appointments/`;

  const bodyData = {
    client_id: parseInt(client_id),
    professional_id: parseInt(professional_id),
    service_id: parseInt(service_id),
    start_time: start_time,
  };

  console.log(`[API] Criando agendamento em: ${url}`, bodyData);

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(bodyData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao criar agendamento.';
    throw new Error(message);
  }

  return await response.json();
}

/**
 * 14. LISTAR AGENDAMENTOS DO USUÁRIO (GET /appointments/)
 */
export async function fetchAppointments(token) {
  const url = `${API_BASE_URL}/appointments/?limit=100`;

  console.log(`[API] Buscando agendamentos em: ${url}`);

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao obter lista de agendamentos.';
    throw new Error(message);
  }

  return await response.json();
}

/**
 * 15. CANCELAR AGENDAMENTO (DELETE /appointments/{id})
 */
export async function deleteAppointment(appointmentId, token) {
  const url = `${API_BASE_URL}/appointments/${appointmentId}`;

  console.log(`[API] Cancelando agendamento ${appointmentId} em: ${url}`);

  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || 'Falha ao cancelar agendamento.';
    throw new Error(message);
  }

  return await response.json();
}
