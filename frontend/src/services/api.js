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
 * 3. BUSCAR TODOS OS USUÁRIOS (GET /users/)
 * 
 * Usamos esta rota para listar usuários. Não exige permissão no backend,
 * mas utilizaremos para encontrar os detalhes do usuário logado através do e-mail.
 */
export async function fetchUsers() {
  const url = `${API_BASE_URL}/users/?offset=0&limit=100`;

  console.log(`[API] Buscando lista de usuários de: ${url}`);

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
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
 * Fluxo didático:
 * - A partir do token de acesso salvo, decodificamos o e-mail do usuário.
 * - Fazemos a busca dos usuários cadastrados.
 * - Filtramos a lista para retornar o usuário que coincide com o e-mail decodificado do token.
 */
export async function fetchLoggedInUserProfile(token) {
  const payload = decodeTokenPayload(token);
  if (!payload || !payload.sub) {
    throw new Error('Token inválido ou expirado.');
  }

  const loggedInEmail = payload.sub; // O email está no campo 'sub'
  console.log(`[API] Email extraído do token: ${loggedInEmail}. Buscando dados cadastrais...`);

  const data = await fetchUsers();
  const matchedUser = data.users.find(user => user.email === loggedInEmail);

  if (!matchedUser) {
    throw new Error('Perfil do usuário não encontrado na lista do servidor.');
  }

  return matchedUser;
}
