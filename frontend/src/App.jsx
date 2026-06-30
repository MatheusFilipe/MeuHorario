import { useState, useEffect } from 'react';
import { 
  Scissors, 
  Clock, 
  MapPin, 
  User, 
  LogIn, 
  LogOut, 
  Lock, 
  Mail, 
  Star, 
  Menu, 
  X, 
  ArrowRight, 
  ShieldCheck, 
  Calendar,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';
import * as api from './services/api';
import './App.css'; // Mantemos a importação para evitar quebras, mas usaremos Tailwind prioritariamente

function App() {
  // --- ESTADOS DO USUÁRIO E AUTENTICAÇÃO ---
  const [token, setToken] = useState(localStorage.getItem('meuhorario_token') || null);
  const [currentUser, setCurrentUser] = useState(null);
  const [isLoadingUser, setIsLoadingUser] = useState(false);

  // --- ESTADOS DE CONTROLE DE INTERFACE ---
  const [activeModal, setActiveModal] = useState(null); // 'login', 'register', 'scheduling_info', 'profile', 'manage_services', 'manage_users' ou null
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // --- ESTADOS DOS FORMULÁRIOS ---
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  const [regFirstName, setRegFirstName] = useState('');
  const [regLastName, setRegLastName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');

  // --- ESTADOS DE ATUALIZAÇÃO DO PERFIL ---
  const [profFirstName, setProfFirstName] = useState('');
  const [profLastName, setProfLastName] = useState('');
  const [profEmail, setProfEmail] = useState('');
  const [profPassword, setProfPassword] = useState('');

  // --- ESTADOS DE GERENCIAMENTO DE SERVIÇOS ---
  const [services, setServices] = useState([]);
  const [isLoadingServices, setIsLoadingServices] = useState(false);
  const [editingService, setEditingService] = useState(null); // null para criar, objeto do serviço para editar
  const [svcName, setSvcName] = useState('');
  const [svcDuration, setSvcDuration] = useState('');
  const [svcPrice, setSvcPrice] = useState('');

  // --- ESTADOS DE GERENCIAMENTO DE USUÁRIOS ---
  const [usersList, setUsersList] = useState([]);
  const [isLoadingUsersList, setIsLoadingUsersList] = useState(false);

  // --- ESTADOS DE ERRO E CARREGAMENTO DAS APIS ---
  const [apiError, setApiError] = useState('');
  const [apiSuccess, setApiSuccess] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // --- CARREGAMENTO DO PERFIL AO INICIAR OU LOGIN ---
  useEffect(() => {
    // Se temos um token mas não temos os detalhes do usuário na memória, buscamos na API
    if (token && !currentUser) {
      const savedUser = localStorage.getItem('meuhorario_user');
      if (savedUser) {
        // Tentamos ler o usuário cacheado no localStorage primeiro
        try {
          setCurrentUser(JSON.parse(savedUser));
        } catch (e) {
          fetchProfile(token);
        }
      } else {
        fetchProfile(token);
      }
    }
  }, [token, currentUser]);

  // Função didática para buscar o perfil a partir do token
  const fetchProfile = async (authToken) => {
    setIsLoadingUser(true);
    try {
      const userProfile = await api.fetchLoggedInUserProfile(authToken);
      setCurrentUser(userProfile);
      localStorage.setItem('meuhorario_user', JSON.stringify(userProfile));
    } catch (err) {
      console.error("Erro ao sincronizar sessão:", err);
      handleLogout(); // Se o token for inválido, desconecta
    } finally {
      setIsLoadingUser(false);
    }
  };

  // --- AÇÕES DO USUÁRIO ---

  // Função didática de Login
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setApiError('');
    setApiSuccess('');
    setIsSubmitting(true);

    try {
      // 1. Faz chamada POST /auth/token enviando como urlencoded
      const data = await api.login(loginEmail, loginPassword);
      
      // 2. Guarda o token recebido no state e localStorage
      setToken(data.access_token);
      localStorage.setItem('meuhorario_token', data.access_token);

      // 3. Busca o perfil do usuário correspondente
      const userProfile = await api.fetchLoggedInUserProfile(data.access_token);
      setCurrentUser(userProfile);
      localStorage.setItem('meuhorario_user', JSON.stringify(userProfile));

      // 4. Limpa formulário e fecha modal
      setLoginEmail('');
      setLoginPassword('');
      setApiSuccess('Login efetuado com sucesso!');
      setTimeout(() => {
        setActiveModal(null);
        setApiSuccess('');
      }, 1000);
    } catch (err) {
      setApiError(err.message || 'Erro ao fazer login. Verifique seus dados.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Função didática de Cadastro com Auto-Login
  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setApiError('');
    setApiSuccess('');
    setIsSubmitting(true);

    if (!regFirstName || !regLastName || !regEmail || !regPassword) {
      setApiError('Por favor, preencha todos os campos.');
      setIsSubmitting(false);
      return;
    }

    try {
      // 1. Cria a conta do usuário (POST /users/)
      const newUser = await api.registerUser({
        first_name: regFirstName,
        last_name: regLastName,
        email: regEmail,
        password: regPassword
      });

      setApiSuccess('Conta criada com sucesso! Efetuando login...');

      // 2. Auto-login didático: chama a API de token imediatamente após cadastro
      const loginData = await api.login(regEmail, regPassword);
      
      // 3. Salva o token
      setToken(loginData.access_token);
      localStorage.setItem('meuhorario_token', loginData.access_token);

      // 4. Salva o perfil recebido no cadastro (ou busca da API)
      setCurrentUser(newUser);
      localStorage.setItem('meuhorario_user', JSON.stringify(newUser));

      // 5. Reseta campos do formulário
      setRegFirstName('');
      setRegLastName('');
      setRegEmail('');
      setRegPassword('');

      setTimeout(() => {
        setActiveModal(null);
        setApiSuccess('');
      }, 1500);
    } catch (err) {
      setApiError(err.message || 'Erro ao realizar cadastro.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Função didática para Logout
  const handleLogout = () => {
    setToken(null);
    setCurrentUser(null);
    localStorage.removeItem('meuhorario_token');
    localStorage.removeItem('meuhorario_user');
    setMobileMenuOpen(false);
  };

  // Trata clique no menu "Agendar"
  const handleSchedulingClick = (e) => {
    e.preventDefault();
    setMobileMenuOpen(false);
    if (!token) {
      // Se não logado, abre login modal
      setActiveModal('login');
    } else {
      // Se logado, abre modal informativa
      setActiveModal('scheduling_info');
    }
  };

  // Auxiliares para fechar modais e limpar mensagens de erro/sucesso
  const closeModal = () => {
    setActiveModal(null);
    setApiError('');
    setApiSuccess('');
  };

  // --- HANDLERS DO PERFIL DO USUÁRIO ---
  const openProfileModal = () => {
    if (currentUser) {
      setProfFirstName(currentUser.first_name);
      setProfLastName(currentUser.last_name);
      setProfEmail(currentUser.email);
      setProfPassword('');
      setApiError('');
      setApiSuccess('');
      setActiveModal('profile');
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setApiError('');
    setApiSuccess('');
    setIsSubmitting(true);

    if (!profPassword) {
      setApiError('Por favor, digite sua senha atual (ou uma nova) para confirmar as alterações.');
      setIsSubmitting(false);
      return;
    }

    try {
      const updated = await api.updateUser(currentUser.id, {
        first_name: profFirstName,
        last_name: profLastName,
        email: profEmail,
        password: profPassword
      }, token);
      setCurrentUser(updated);
      localStorage.setItem('meuhorario_user', JSON.stringify(updated));
      setApiSuccess('Perfil atualizado com sucesso!');
      setTimeout(() => {
        setActiveModal(null);
      }, 1000);
    } catch (err) {
      setApiError(err.message || 'Erro ao atualizar perfil.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleProfileDelete = async () => {
    if (!window.confirm('Tem certeza absoluta que deseja excluir seu perfil? Esta ação não pode ser desfeita.')) {
      return;
    }
    setApiError('');
    setApiSuccess('');
    setIsSubmitting(true);
    try {
      await api.deleteUser(currentUser.id, token);
      setApiSuccess('Sua conta foi excluída com sucesso.');
      setTimeout(() => {
        handleLogout();
        setActiveModal(null);
      }, 1500);
    } catch (err) {
      setApiError(err.message || 'Erro ao excluir conta.');
      setIsSubmitting(false);
    }
  };

  // --- HANDLERS DO GERENCIAMENTO DE SERVIÇOS (ADMIN) ---
  const loadServices = async () => {
    setIsLoadingServices(true);
    try {
      const data = await api.fetchServices();
      setServices(data.services || []);
    } catch (err) {
      console.error('Erro ao carregar serviços:', err);
    } finally {
      setIsLoadingServices(false);
    }
  };

  const openManageServicesModal = () => {
    setApiError('');
    setApiSuccess('');
    setEditingService(null);
    setSvcName('');
    setSvcDuration('');
    setSvcPrice('');
    setActiveModal('manage_services');
    loadServices();
  };

  const handleServiceSubmit = async (e) => {
    e.preventDefault();
    setApiError('');
    setApiSuccess('');
    setIsSubmitting(true);
    try {
      if (editingService) {
        await api.updateService(editingService.id, {
          name: svcName,
          duration: svcDuration,
          price: svcPrice
        }, token);
        setApiSuccess('Serviço atualizado com sucesso!');
      } else {
        await api.createService({
          name: svcName,
          duration: svcDuration,
          price: svcPrice
        }, token);
        setApiSuccess('Serviço criado com sucesso!');
      }
      setSvcName('');
      setSvcDuration('');
      setSvcPrice('');
      setEditingService(null);
      loadServices();
    } catch (err) {
      setApiError(err.message || 'Erro ao salvar serviço.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const startEditService = (service) => {
    setEditingService(service);
    setSvcName(service.name);
    setSvcDuration(service.duration);
    setSvcPrice(service.price);
  };

  const handleDeleteService = async (serviceId) => {
    if (!window.confirm('Excluir este serviço permanentemente?')) return;
    try {
      await api.deleteService(serviceId, token);
      loadServices();
    } catch (err) {
      alert(err.message || 'Erro ao deletar serviço.');
    }
  };

  // --- HANDLERS DO GERENCIAMENTO DE USUÁRIOS (ADMIN) ---
  const loadUsers = async () => {
    setIsLoadingUsersList(true);
    try {
      const data = await api.fetchUsers(token);
      setUsersList(data.users || []);
    } catch (err) {
      console.error('Erro ao carregar usuários:', err);
    } finally {
      setIsLoadingUsersList(false);
    }
  };

  const openManageUsersModal = () => {
    setApiError('');
    setApiSuccess('');
    setActiveModal('manage_users');
    loadUsers();
  };

  const handleDeleteUser = async (userId) => {
    if (userId === currentUser.id) {
      alert('Você não pode excluir a sua própria conta de administrador por esta tela. Use as configurações de perfil.');
      return;
    }
    if (!window.confirm('Tem certeza que deseja excluir este usuário permanentemente?')) return;
    try {
      await api.deleteUser(userId, token);
      loadUsers();
    } catch (err) {
      alert(err.message || 'Erro ao excluir usuário.');
    }
  };

  return (
    <div className="min-h-screen bg-[#121214] text-gray-100 flex flex-col selection:bg-primary selection:text-black">
      
      {/* ========================================================================= */}
      {/* 1. HEADER & NAVIGATION */}
      {/* ========================================================================= */}
      <header className="sticky top-0 z-40 bg-[#121214]/90 backdrop-blur-md border-b border-dark-border transition-all duration-300">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          
          {/* LOGO E NOME */}
          <a href="#" className="flex items-center gap-2 group">
            <div className="p-2.5 bg-dark-card border border-primary/20 rounded-xl group-hover:border-primary transition-colors">
              <Scissors className="w-6 h-6 text-primary rotate-90 group-hover:rotate-45 transition-transform duration-300" />
            </div>
            <div>
              <span className="font-serif text-xl font-bold tracking-wider text-gray-100 block">PREMIUM BARBEARIA</span>
              <span className="text-[10px] text-primary font-sans tracking-[0.2em] block -mt-1">INTEGRADA AO MEUHORÁRIO</span>
            </div>
          </a>

          {/* NAV DESKTOP */}
          <nav className="hidden md:flex items-center gap-8 font-medium">
            <a href="#sobre" className="text-gray-300 hover:text-primary transition-colors">Sobre</a>
            <a 
              href="#agendar" 
              onClick={handleSchedulingClick} 
              className="text-gray-300 hover:text-primary transition-colors flex items-center gap-1.5"
            >
              <Calendar className="w-4 h-4 text-primary" />
              Agendar
            </a>
            
            {token && currentUser && currentUser.role === 'admin' && (
              <>
                <button 
                  onClick={openManageServicesModal} 
                  className="text-gray-300 hover:text-primary transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  Serviços
                </button>
                <button 
                  onClick={openManageUsersModal} 
                  className="text-gray-300 hover:text-primary transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  Usuários
                </button>
              </>
            )}

            <div className="h-6 w-[1px] bg-dark-border"></div>

            {/* SE LOGADO: Mensagem + Botão Sair */}
            {token && currentUser ? (
              <div className="flex items-center gap-4">
                <button 
                  onClick={openProfileModal}
                  className="text-sm text-gray-300 hover:text-primary transition-colors cursor-pointer"
                >
                  Bem-vindo, <strong className="text-primary hover:underline">{currentUser.first_name}</strong>!
                </button>
                <button 
                  onClick={handleLogout} 
                  className="flex items-center gap-1 text-xs px-3.5 py-2 rounded-lg bg-red-950/40 text-red-400 border border-red-900/30 hover:bg-red-900 hover:text-white transition-all cursor-pointer"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  Sair
                </button>
              </div>
            ) : (
              // SE NÃO LOGADO: Botão Entrar
              <button 
                onClick={() => setActiveModal('login')} 
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl border border-primary/30 text-primary hover:bg-primary hover:text-black hover:border-primary transition-all duration-300 cursor-pointer text-sm font-semibold"
              >
                <LogIn className="w-4 h-4" />
                Entrar
              </button>
            )}
          </nav>

          {/* MENU MOBILE TOGGLE */}
          <button 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)} 
            className="md:hidden p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-card border border-dark-border"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* NAV MOBILE EXPANDIDA */}
        {mobileMenuOpen && (
          <div className="md:hidden px-4 pt-2 pb-6 border-b border-dark-border bg-[#121214] flex flex-col gap-4 animate-fadeIn">
            <a 
              href="#sobre" 
              onClick={() => setMobileMenuOpen(false)}
              className="text-lg py-2 border-b border-dark-border/40 text-gray-300 hover:text-primary transition-colors"
            >
              Sobre
            </a>
            <a 
              href="#agendar" 
              onClick={handleSchedulingClick}
              className="text-lg py-2 border-b border-dark-border/40 text-gray-300 hover:text-primary transition-colors flex items-center gap-2"
            >
              <Calendar className="w-5 h-5 text-primary" />
              Agendar
            </a>

            {token && currentUser && currentUser.role === 'admin' && (
              <>
                <button 
                  onClick={() => { setMobileMenuOpen(false); openManageServicesModal(); }}
                  className="text-left text-lg py-2 border-b border-dark-border/40 text-gray-300 hover:text-primary transition-colors cursor-pointer"
                >
                  Gerenciar Serviços
                </button>
                <button 
                  onClick={() => { setMobileMenuOpen(false); openManageUsersModal(); }}
                  className="text-left text-lg py-2 border-b border-dark-border/40 text-gray-300 hover:text-primary transition-colors cursor-pointer"
                >
                  Gerenciar Usuários
                </button>
              </>
            )}

            {token && currentUser ? (
              <div className="pt-2 flex flex-col gap-3">
                <button 
                  onClick={() => { setMobileMenuOpen(false); openProfileModal(); }}
                  className="text-left text-gray-300 hover:text-primary transition-colors cursor-pointer"
                >
                  Bem-vindo, <strong className="text-primary hover:underline">{currentUser.first_name}</strong>!
                </button>
                <button 
                  onClick={handleLogout} 
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-red-950/40 text-red-400 border border-red-900/30 hover:bg-red-900 hover:text-white transition-all cursor-pointer"
                >
                  <LogOut className="w-4 h-4" />
                  Sair da Conta
                </button>
              </div>
            ) : (
              <button 
                onClick={() => { setMobileMenuOpen(false); setActiveModal('login'); }}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border border-primary text-primary hover:bg-primary hover:text-black transition-all cursor-pointer font-bold mt-2"
              >
                <LogIn className="w-4 h-4" />
                Entrar / Criar Conta
              </button>
            )}
          </div>
        )}
      </header>

      {/* ========================================================================= */}
      {/* 2. HERO SECTION */}
      {/* ========================================================================= */}
      <section className="relative overflow-hidden pt-12 pb-20 md:py-32 flex items-center justify-center border-b border-dark-border">
        {/* Efeito de luz ao fundo */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px] pointer-events-none"></div>

        <div className="max-w-4xl mx-auto px-4 text-center relative z-10">
          
          {/* Badge */}
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-bold uppercase tracking-wider mb-6">
            <Star className="w-3.5 h-3.5 fill-primary" />
            Experiência Premium de Barbearia
          </div>

          <h1 className="font-serif text-5xl md:text-7xl font-bold tracking-tight text-white mb-6 leading-none">
            Estilo Clássico.<br />
            <span className="text-primary font-serif italic">Cuidados Modernos.</span>
          </h1>

          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed font-light">
            Onde a tradição da navalha se encontra com a sofisticação moderna. Viva a experiência de cuidar do seu visual com os melhores barbeiros da região.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button 
              onClick={handleSchedulingClick}
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-primary hover:bg-primary-hover text-black font-bold text-base shadow-lg shadow-primary/20 hover:shadow-primary/30 hover:-translate-y-0.5 transition-all duration-300 flex items-center justify-center gap-2 cursor-pointer"
            >
              <Calendar className="w-5 h-5" />
              Agendar Horário
            </button>
            <a 
              href="#sobre" 
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-dark-card hover:bg-dark-card/80 border border-dark-border text-gray-300 hover:text-white transition-all text-center block font-semibold"
            >
              Conhecer a Barbearia
            </a>
          </div>
        </div>
      </section>

      {/* ========================================================================= */}
      {/* 3. SEÇÃO SOBRE (ABOUT) */}
      {/* ========================================================================= */}
      <section id="sobre" className="py-20 bg-dark-card border-b border-dark-border scroll-mt-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          
          <div className="text-center max-w-xl mx-auto mb-16">
            <h2 className="font-serif text-3xl md:text-4xl font-bold text-white mb-4">Sobre a Nossa Casa</h2>
            <div className="h-1 w-20 bg-primary mx-auto rounded-full mb-4"></div>
            <p className="text-gray-400">
              Conheça a nossa história, nossos barbeiros especialistas e onde nos encontrar.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center mb-20">
            {/* História Text */}
            <div className="space-y-6">
              <span className="text-xs text-primary font-bold tracking-widest uppercase block">Nossa História</span>
              <h3 className="font-serif text-2xl font-bold text-white">Tradição, Excelência e Hospitalidade</h3>
              <p className="text-gray-400 leading-relaxed font-light">
                Fundada em 2018, a <strong>Premium Barbearia</strong> nasceu com o propósito de resgatar o valor clássico das barbearias tradicionais, unindo-o às técnicas contemporâneas de corte e estética masculina.
              </p>
              <p className="text-gray-400 leading-relaxed font-light">
                Aqui, cada atendimento é tratado como um ritual de relaxamento e autocuidado. Oferecemos um ambiente climatizado, café premium de cortesia, conversa agradável e, claro, profissionais obstinados com a perfeição de cada traço de barba e corte.
              </p>
              <div className="p-4 border-l-2 border-primary bg-primary/5 rounded-r-xl">
                <p className="italic text-gray-300 font-light text-sm">
                  "Não vendemos apenas cortes de cabelo e barba, proporcionamos uma elevação de autoimagem e confiança."
                </p>
              </div>
            </div>

            {/* Imagem Placeholder Estilizada */}
            <div className="relative aspect-video lg:aspect-square bg-gradient-to-tr from-black to-neutral-900 border border-primary/20 rounded-2xl overflow-hidden flex items-center justify-center p-8 group">
              <div className="absolute inset-0 bg-cover bg-center opacity-40 group-hover:scale-105 transition-transform duration-700 bg-[url('https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&q=80&w=800')]" />
              <div className="absolute inset-0 bg-gradient-to-t from-[#121214] via-[#121214]/60 to-transparent" />
              <div className="relative text-center z-10 space-y-2">
                <Scissors className="w-12 h-12 text-primary mx-auto mb-4" />
                <h4 className="font-serif text-lg font-bold text-white uppercase tracking-widest">Estilo Clássico</h4>
                <p className="text-xs text-gray-400 font-sans tracking-wide">Tesouras afiadas • Toalha Quente • Navalha Afiada</p>
              </div>
            </div>
          </div>

          {/* PROFISSIONAIS */}
          <div className="mb-20">
            <h3 className="font-serif text-2xl font-bold text-white text-center mb-10 flex items-center justify-center gap-2">
              <Scissors className="w-5 h-5 text-primary rotate-90" />
              Nossos Profissionais
            </h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
              {/* Profissional 1 */}
              <div className="bg-[#121214] border border-dark-border rounded-2xl p-6 text-center hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 group">
                <div className="w-24 h-24 rounded-full bg-dark-card border border-primary/30 mx-auto mb-4 flex items-center justify-center group-hover:border-primary transition-colors overflow-hidden">
                  {/* Avatar inicial */}
                  <span className="font-serif text-3xl text-primary font-bold">MS</span>
                </div>
                <h4 className="font-serif text-lg font-bold text-white">Márcio Silva</h4>
                <span className="text-xs text-primary font-semibold tracking-wider uppercase block mb-3">Master Barber & Fundador</span>
                <p className="text-xs text-gray-400 font-light">Especialista em barbas esculpidas na navalha clássica e cortes masculinos clássicos.</p>
              </div>

              {/* Profissional 2 */}
              <div className="bg-[#121214] border border-dark-border rounded-2xl p-6 text-center hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 group">
                <div className="w-24 h-24 rounded-full bg-dark-card border border-primary/30 mx-auto mb-4 flex items-center justify-center group-hover:border-primary transition-colors overflow-hidden">
                  <span className="font-serif text-3xl text-primary font-bold">BC</span>
                </div>
                <h4 className="font-serif text-lg font-bold text-white">Bruno Costa</h4>
                <span className="text-xs text-primary font-semibold tracking-wider uppercase block mb-3">Visagista Especialista</span>
                <p className="text-xs text-gray-400 font-light">Mestre em degradês (Fades) modernos e cortes despojados com texturizações atuais.</p>
              </div>

              {/* Profissional 3 */}
              <div className="bg-[#121214] border border-dark-border rounded-2xl p-6 text-center hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 group">
                <div className="w-24 h-24 rounded-full bg-dark-card border border-primary/30 mx-auto mb-4 flex items-center justify-center group-hover:border-primary transition-colors overflow-hidden">
                  <span className="font-serif text-3xl text-primary font-bold">LL</span>
                </div>
                <h4 className="font-serif text-lg font-bold text-white">Lucas Lima</h4>
                <span className="text-xs text-primary font-semibold tracking-wider uppercase block mb-3">Hair Stylist Masculino</span>
                <p className="text-xs text-gray-400 font-light">Especialista em colorimetria masculina, platinados, hidratações e selagem capilar.</p>
              </div>
            </div>
          </div>

          {/* HORÁRIOS DE ATENDIMENTO E GOOGLE MAPS */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Tabela de Horários */}
            <div className="bg-[#121214] border border-dark-border rounded-2xl p-6 lg:col-span-1 flex flex-col justify-between">
              <div>
                <h3 className="font-serif text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-primary" />
                  Horários
                </h3>
                <ul className="space-y-4">
                  <li className="flex justify-between items-center pb-2 border-b border-dark-border/40">
                    <span className="text-sm font-medium text-gray-300">Segunda-feira</span>
                    <span className="text-sm text-primary font-bold">09:00 - 20:00</span>
                  </li>
                  <li className="flex justify-between items-center pb-2 border-b border-dark-border/40">
                    <span className="text-sm font-medium text-gray-300">Terça a Sexta</span>
                    <span className="text-sm text-primary font-bold">09:00 - 20:00</span>
                  </li>
                  <li className="flex justify-between items-center pb-2 border-b border-dark-border/40">
                    <span className="text-sm font-medium text-gray-300">Sábado</span>
                    <span className="text-sm text-primary font-bold">08:00 - 18:00</span>
                  </li>
                  <li className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-500">Domingo</span>
                    <span className="text-sm text-gray-500 italic">Fechado</span>
                  </li>
                </ul>
              </div>

              <div className="mt-8 pt-6 border-t border-dark-border/40 flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <ShieldCheck className="w-5 h-5 text-primary" />
                </div>
                <p className="text-[11px] text-gray-400 leading-tight">
                  Atendimento preferencial com agendamento prévio. Tolerância de 10 minutos para atrasos.
                </p>
              </div>
            </div>

            {/* Google Maps Iframe */}
            <div className="bg-[#121214] border border-dark-border rounded-2xl p-6 lg:col-span-2 flex flex-col justify-between h-full">
              <h3 className="font-serif text-xl font-bold text-white mb-4 flex items-center gap-2">
                <MapPin className="w-5 h-5 text-primary" />
                Nossa Localização
              </h3>
              <p className="text-sm text-gray-400 mb-4 font-light">
                Av. Paulista, 1000 - Bela Vista, São Paulo - SP, 01310-100 (Edifício Paulista Business)
              </p>
              <div className="w-full h-64 rounded-xl overflow-hidden border border-dark-border bg-dark-card">
                <iframe
                  title="Mapa de Localização"
                  src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3657.1975870075344!2d-46.654308523789495!3d-23.561349561845187!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x94ce59c8da0aa315%3A0xd59f9431de397d51!2sAv.%20Paulista%2C%201000%20-%20Bela%20Vista%2C%20S%C3%A3o%20Paulo%20-%20SP%2C%2001310-100!5e0!3m2!1spt-BR!2sbr!4v1700000000000!5m2!1spt-BR!2sbr"
                  width="100%"
                  height="100%"
                  style={{ border: 0 }}
                  allowFullScreen=""
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                ></iframe>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* ========================================================================= */}
      {/* FOOTER */}
      {/* ========================================================================= */}
      <footer className="mt-auto py-8 bg-[#0a0a0c] border-t border-dark-border">
        <div className="max-w-6xl mx-auto px-4 text-center space-y-4">
          <p className="text-sm text-gray-500 font-light">
            © {new Date().getFullYear()} Premium Barbearia. Todos os direitos reservados.
          </p>
          <p className="text-[10px] text-gray-600 font-sans tracking-widest">
            PROJETO DE API REST & FRONTED PARA APRENDIZADO DIDÁTICO
          </p>
        </div>
      </footer>

      {/* ========================================================================= */}
      {/* MODAL 1: LOGIN */}
      {/* ========================================================================= */}
      {activeModal === 'login' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-md bg-dark-card border border-dark-border rounded-2xl p-6 sm:p-8 relative shadow-2xl animate-scaleIn">
            
            {/* Fechar botão */}
            <button 
              onClick={closeModal}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#121214] border border-dark-border"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Cabeçalho do Modal */}
            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-primary/10 border border-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <LogIn className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-serif text-xl font-bold text-white">Entrar na Premium Barbearia</h3>
              <p className="text-xs text-gray-400 mt-1">Acesse sua conta para gerenciar seus agendamentos</p>
            </div>

            {/* Notificações de Erro / Sucesso */}
            {apiError && (
              <div className="mb-4 p-3 rounded-lg bg-red-950/40 border border-red-900/30 text-red-400 text-xs flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{apiError}</span>
              </div>
            )}
            {apiSuccess && (
              <div className="mb-4 p-3 rounded-lg bg-emerald-950/40 border border-emerald-900/30 text-emerald-400 text-xs flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{apiSuccess}</span>
              </div>
            )}

            {/* Formulário */}
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-semibold text-gray-300 block mb-1">E-mail</label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input 
                    type="email" 
                    required
                    placeholder="voce@exemplo.com"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-[#121214] border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-300 block mb-1">Senha</label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input 
                    type="password" 
                    required
                    placeholder="••••••••"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-[#121214] border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
              </div>

              <button 
                type="submit" 
                disabled={isSubmitting}
                className="w-full py-3.5 rounded-xl bg-primary hover:bg-primary-hover disabled:bg-primary/50 text-black font-bold text-sm transition-colors cursor-pointer mt-6 flex items-center justify-center gap-2"
              >
                {isSubmitting ? 'Entrando...' : 'Entrar'}
                {!isSubmitting && <ArrowRight className="w-4 h-4" />}
              </button>
            </form>

            {/* Alternar para Cadastro */}
            <div className="mt-6 pt-4 border-t border-dark-border/40 text-center text-xs text-gray-400">
              Não tem uma conta ainda?{' '}
              <button 
                onClick={() => { setApiError(''); setApiSuccess(''); setActiveModal('register'); }}
                className="text-primary hover:underline font-semibold cursor-pointer"
              >
                Criar conta
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 2: CADASTRO */}
      {/* ========================================================================= */}
      {activeModal === 'register' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-md bg-dark-card border border-dark-border rounded-2xl p-6 sm:p-8 relative shadow-2xl animate-scaleIn">
            
            <button 
              onClick={closeModal}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#121214] border border-dark-border"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="text-center mb-5">
              <div className="w-12 h-12 bg-primary/10 border border-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <User className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-serif text-xl font-bold text-white">Criar Conta</h3>
              <p className="text-xs text-gray-400 mt-1">Cadastre-se para reservar serviços na barbearia</p>
            </div>

            {apiError && (
              <div className="mb-4 p-3 rounded-lg bg-red-950/40 border border-red-900/30 text-red-400 text-xs flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{apiError}</span>
              </div>
            )}
            {apiSuccess && (
              <div className="mb-4 p-3 rounded-lg bg-emerald-950/40 border border-emerald-900/30 text-emerald-400 text-xs flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{apiSuccess}</span>
              </div>
            )}

            <form onSubmit={handleRegisterSubmit} className="space-y-3.5">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-gray-300 block mb-1">Nome</label>
                  <input 
                    type="text" 
                    required
                    placeholder="João"
                    value={regFirstName}
                    onChange={(e) => setRegFirstName(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#121214] border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-gray-300 block mb-1">Sobrenome</label>
                  <input 
                    type="text" 
                    required
                    placeholder="Silva"
                    value={regLastName}
                    onChange={(e) => setRegLastName(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#121214] border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-300 block mb-1">E-mail</label>
                <div className="relative">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input 
                    type="email" 
                    required
                    placeholder="joao@exemplo.com"
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#121214] border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-300 block mb-1">Senha</label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input 
                    type="password" 
                    required
                    placeholder="Crie uma senha forte"
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#121214] border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
              </div>

              <button 
                type="submit" 
                disabled={isSubmitting}
                className="w-full py-3.5 rounded-xl bg-primary hover:bg-primary-hover disabled:bg-primary/50 text-black font-bold text-sm transition-colors cursor-pointer mt-4 flex items-center justify-center gap-2"
              >
                {isSubmitting ? 'Cadastrando...' : 'Cadastrar e Entrar'}
                {!isSubmitting && <ArrowRight className="w-4 h-4" />}
              </button>
            </form>

            <div className="mt-5 pt-4 border-t border-dark-border/40 text-center text-xs text-gray-400">
              Já tem cadastro?{' '}
              <button 
                onClick={() => { setApiError(''); setApiSuccess(''); setActiveModal('login'); }}
                className="text-primary hover:underline font-semibold cursor-pointer"
              >
                Fazer login
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 3: INFORMAÇÕES DE AGENDAMENTO */}
      {/* ========================================================================= */}
      {activeModal === 'scheduling_info' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-md bg-dark-card border border-dark-border rounded-2xl p-6 sm:p-8 relative shadow-2xl animate-scaleIn text-center">
            
            <button 
              onClick={closeModal}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#121214] border border-dark-border"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="w-16 h-16 bg-primary/10 border border-primary/20 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
              <Calendar className="w-8 h-8 text-primary" />
            </div>

            <h3 className="font-serif text-2xl font-bold text-white mb-2">Agendamentos Online</h3>
            
            <div className="h-0.5 w-12 bg-primary mx-auto my-3 rounded-full"></div>

            <p className="text-sm text-gray-300 leading-relaxed font-light mb-6">
              Olá, <strong className="text-primary">{currentUser?.first_name}</strong>! <br />
              Atualmente estamos integrando nossa plataforma de agendamento online.
            </p>

            <div className="p-4 bg-[#121214] border border-dark-border rounded-xl mb-6 text-xs text-left text-gray-400 space-y-2">
              <p className="font-semibold text-gray-300">Próximos passos do projeto:</p>
              <ul className="list-disc list-inside space-y-1.5">
                <li>Integração com a rota <code className="text-xs bg-dark-card px-1 py-0.5 text-primary">GET /services/</code> para listar serviços</li>
                <li>Integração com <code className="text-xs bg-dark-card px-1 py-0.5 text-primary">POST /appointments/</code> para marcar o horário</li>
                <li>Confirmação e exibição dos agendamentos marcados</li>
              </ul>
            </div>

            <button 
              onClick={closeModal}
              className="w-full py-3.5 rounded-xl bg-primary hover:bg-primary-hover text-black font-bold text-sm transition-colors cursor-pointer"
            >
              Entendido, aguardo novidades!
            </button>

          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 4: PERFIL DO USUÁRIO */}
      {/* ========================================================================= */}
      {activeModal === 'profile' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-md bg-dark-card border border-dark-border rounded-2xl p-6 sm:p-8 relative shadow-2xl animate-scaleIn">
            
            <button 
              onClick={closeModal}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#121214] border border-dark-border"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="text-center mb-5">
              <div className="w-12 h-12 bg-primary/10 border border-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <User className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-serif text-xl font-bold text-white">Minhas Configurações</h3>
              <p className="text-xs text-gray-400 mt-1">Atualize seus dados pessoais ou exclua seu perfil</p>
            </div>

            {apiError && (
              <div className="mb-4 p-3 rounded-lg bg-red-950/40 border border-red-900/30 text-red-400 text-xs flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{apiError}</span>
              </div>
            )}
            {apiSuccess && (
              <div className="mb-4 p-3 rounded-lg bg-emerald-950/40 border border-emerald-900/30 text-emerald-400 text-xs flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{apiSuccess}</span>
              </div>
            )}

            <form onSubmit={handleProfileUpdate} className="space-y-3.5">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-gray-300 block mb-1">Nome</label>
                  <input 
                    type="text" 
                    required
                    value={profFirstName}
                    onChange={(e) => setProfFirstName(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#121214] border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-gray-300 block mb-1">Sobrenome</label>
                  <input 
                    type="text" 
                    required
                    value={profLastName}
                    onChange={(e) => setProfLastName(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#121214] border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-300 block mb-1">E-mail</label>
                <input 
                  type="email" 
                  required
                  value={profEmail}
                  onChange={(e) => setProfEmail(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#121214] border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-gray-300 block mb-1">Confirmar Senha</label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                  <input 
                    type="password" 
                    required
                    placeholder="Digite sua senha para salvar"
                    value={profPassword}
                    onChange={(e) => setProfPassword(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#121214] border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <button 
                  type="button"
                  onClick={handleProfileDelete}
                  disabled={isSubmitting}
                  className="flex-1 py-3 rounded-xl bg-red-950/40 hover:bg-red-900 border border-red-900/30 text-red-400 hover:text-white text-sm font-semibold transition-colors cursor-pointer"
                >
                  Excluir Conta
                </button>
                <button 
                  type="submit" 
                  disabled={isSubmitting}
                  className="flex-1 py-3 rounded-xl bg-primary hover:bg-primary-hover text-black font-semibold text-sm transition-colors cursor-pointer"
                >
                  {isSubmitting ? 'Salvando...' : 'Salvar'}
                </button>
              </div>
            </form>

          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 5: GERENCIAMENTO DE SERVIÇOS (ADMIN) */}
      {/* ========================================================================= */}
      {activeModal === 'manage_services' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-2xl bg-dark-card border border-dark-border rounded-2xl p-6 sm:p-8 relative shadow-2xl animate-scaleIn max-h-[90vh] overflow-y-auto">
            
            <button 
              onClick={closeModal}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#121214] border border-dark-border"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-primary/10 border border-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <Scissors className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-serif text-xl font-bold text-white">Gerenciamento de Serviços</h3>
              <p className="text-xs text-gray-400 mt-1">Crie, edite ou exclua serviços oferecidos pela Premium Barbearia</p>
            </div>

            {apiError && (
              <div className="mb-4 p-3 rounded-lg bg-red-950/40 border border-red-900/30 text-red-400 text-xs flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{apiError}</span>
              </div>
            )}
            {apiSuccess && (
              <div className="mb-4 p-3 rounded-lg bg-emerald-950/40 border border-emerald-900/30 text-emerald-400 text-xs flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{apiSuccess}</span>
              </div>
            )}

            {/* FORMULÁRIO DE CRIAÇÃO / EDIÇÃO */}
            <form onSubmit={handleServiceSubmit} className="mb-8 p-4 bg-[#121214] border border-dark-border rounded-xl space-y-4">
              <h4 className="text-sm font-semibold text-primary">
                {editingService ? `Editar Serviço: ${editingService.name}` : 'Criar Novo Serviço'}
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <label className="text-[10px] uppercase tracking-wider text-gray-400 block mb-1">Nome do Serviço</label>
                  <input 
                    type="text" 
                    required
                    placeholder="Ex: Corte Degradê"
                    value={svcName}
                    onChange={(e) => setSvcName(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-dark-card border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="text-[10px] uppercase tracking-wider text-gray-400 block mb-1">Duração (minutos)</label>
                  <input 
                    type="number" 
                    required
                    placeholder="Ex: 30"
                    value={svcDuration}
                    onChange={(e) => setSvcDuration(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-dark-card border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
                <div>
                  <label className="text-[10px] uppercase tracking-wider text-gray-400 block mb-1">Preço (R$)</label>
                  <input 
                    type="number" 
                    step="0.01"
                    required
                    placeholder="Ex: 45.00"
                    value={svcPrice}
                    onChange={(e) => setSvcPrice(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-dark-card border border-dark-border focus:border-primary/50 text-sm outline-none transition-colors"
                  />
                </div>
              </div>
              <div className="flex gap-2 justify-end">
                {editingService && (
                  <button 
                    type="button" 
                    onClick={() => { setEditingService(null); setSvcName(''); setSvcDuration(''); setSvcPrice(''); }}
                    className="px-4 py-2 text-xs border border-dark-border rounded-lg text-gray-400 hover:text-white cursor-pointer"
                  >
                    Cancelar
                  </button>
                )}
                <button 
                  type="submit" 
                  disabled={isSubmitting}
                  className="px-5 py-2 text-xs bg-primary hover:bg-primary-hover text-black font-semibold rounded-lg transition-colors cursor-pointer"
                >
                  {isSubmitting ? 'Salvando...' : editingService ? 'Atualizar Serviço' : 'Criar Serviço'}
                </button>
              </div>
            </form>

            {/* LISTA DE SERVIÇOS */}
            <div>
              <h4 className="text-sm font-semibold text-gray-200 mb-3">Serviços Cadastrados</h4>
              {isLoadingServices ? (
                <p className="text-xs text-gray-500 text-center py-4">Carregando serviços...</p>
              ) : services.length === 0 ? (
                <p className="text-xs text-gray-500 text-center py-4">Nenhum serviço cadastrado.</p>
              ) : (
                <div className="border border-dark-border rounded-xl overflow-hidden divide-y divide-dark-border">
                  {services.map((service) => (
                    <div key={service.id} className="flex justify-between items-center p-3.5 hover:bg-[#121214] transition-colors">
                      <div>
                        <p className="font-semibold text-sm text-gray-100">{service.name}</p>
                        <p className="text-xs text-gray-400">{service.duration} min • R$ {service.price.toFixed(2)}</p>
                      </div>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => startEditService(service)}
                          className="px-3 py-1.5 text-[10px] bg-[#121214] hover:bg-dark-border text-gray-300 hover:text-white border border-dark-border rounded-md cursor-pointer transition-colors"
                        >
                          Editar
                        </button>
                        <button 
                          onClick={() => handleDeleteService(service.id)}
                          className="px-3 py-1.5 text-[10px] bg-red-950/20 hover:bg-red-900/40 text-red-400 hover:text-red-200 border border-red-900/30 rounded-md cursor-pointer transition-colors"
                        >
                          Deletar
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL 6: GERENCIAMENTO DE USUÁRIOS (ADMIN) */}
      {/* ========================================================================= */}
      {activeModal === 'manage_users' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-2xl bg-dark-card border border-dark-border rounded-2xl p-6 sm:p-8 relative shadow-2xl animate-scaleIn max-h-[90vh] overflow-y-auto">
            
            <button 
              onClick={closeModal}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#121214] border border-dark-border"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="text-center mb-6">
              <div className="w-12 h-12 bg-primary/10 border border-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
                <User className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-serif text-xl font-bold text-white">Gerenciamento de Usuários</h3>
              <p className="text-xs text-gray-400 mt-1">Visualize e gerencie os usuários registrados na aplicação</p>
            </div>

            {/* LISTA DE USUÁRIOS */}
            <div>
              {isLoadingUsersList ? (
                <p className="text-xs text-gray-500 text-center py-4">Carregando usuários...</p>
              ) : usersList.length === 0 ? (
                <p className="text-xs text-gray-500 text-center py-4">Nenhum usuário cadastrado.</p>
              ) : (
                <div className="border border-dark-border rounded-xl overflow-hidden divide-y divide-dark-border">
                  {usersList.map((user) => (
                    <div key={user.id} className="flex justify-between items-center p-3.5 hover:bg-[#121214] transition-colors">
                      <div>
                        <p className="font-semibold text-sm text-gray-100">
                          {user.first_name} {user.last_name}{' '}
                          <span className={`ml-2 text-[10px] px-2 py-0.5 rounded-full font-sans font-bold uppercase ${
                            user.role === 'admin' 
                              ? 'bg-primary/20 text-primary border border-primary/30' 
                              : user.role === 'professional' 
                                ? 'bg-indigo-950/40 text-indigo-400 border border-indigo-900/30'
                                : 'bg-gray-800 text-gray-400 border border-gray-700'
                          }`}>
                            {user.role}
                          </span>
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">{user.email}</p>
                      </div>
                      <div>
                        {user.id !== currentUser.id ? (
                          <button 
                            onClick={() => handleDeleteUser(user.id)}
                            className="px-3 py-1.5 text-[10px] bg-red-950/20 hover:bg-red-900/40 text-red-400 hover:text-red-200 border border-red-900/30 rounded-md cursor-pointer transition-colors"
                          >
                            Excluir
                          </button>
                        ) : (
                          <span className="text-[10px] text-gray-600 italic">Você (Admin)</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>
      )}

    </div>
  );
}

export default App;
