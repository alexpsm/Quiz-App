import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Phone, Camera } from 'lucide-react';
import { users, clubs } from '../lib/api';
import { PoweredByScore90 } from '../components/Score90Logo';
import { useAuth } from '../context/AuthContext';
import {
  Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue
} from '../components/ui/select';

const FOOTBALL_AVATARS = [
  { seed: 'Ronaldo', label: 'Striker' },
  { seed: 'Messi', label: 'Playmaker' },
  { seed: 'Mbappe', label: 'Winger' },
  { seed: 'Haaland', label: 'Forward' },
  { seed: 'DeBruyne', label: 'Midfield' },
  { seed: 'VanDijk', label: 'Defender' },
  { seed: 'Modric', label: 'Captain' },
  { seed: 'Neuer', label: 'Keeper' },
];

const COUNTRIES = [
  "Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda","Argentina","Armenia","Australia","Austria",
  "Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bhutan",
  "Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria","Burkina Faso","Burundi","Cabo Verde","Cambodia",
  "Cameroon","Canada","Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo","Costa Rica",
  "Croatia","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt",
  "El Salvador","Equatorial Guinea","Eritrea","Estonia","Eswatini","Ethiopia","Fiji","Finland","France","Gabon",
  "Gambia","Georgia","Germany","Ghana","Greece","Grenada","Guatemala","Guinea","Guinea-Bissau","Guyana",
  "Haiti","Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Israel",
  "Italy","Ivory Coast","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Kuwait","Kyrgyzstan",
  "Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Madagascar",
  "Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia",
  "Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar","Namibia","Nauru","Nepal",
  "Netherlands","New Zealand","Nicaragua","Niger","Nigeria","North Korea","North Macedonia","Norway","Oman","Pakistan",
  "Palau","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar",
  "Romania","Russia","Rwanda","Saint Kitts and Nevis","Saint Lucia","Saint Vincent and the Grenadines","Samoa","San Marino","Sao Tome and Principe","Saudi Arabia",
  "Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa",
  "South Korea","South Sudan","Spain","Sri Lanka","Sudan","Suriname","Sweden","Switzerland","Syria","Taiwan",
  "Tajikistan","Tanzania","Thailand","Timor-Leste","Togo","Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan",
  "Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States","Uruguay","Uzbekistan","Vanuatu","Vatican City",
  "Venezuela","Vietnam","Yemen","Zambia","Zimbabwe"
];

const AGES = Array.from({ length: 88 }, (_, i) => String(i + 12));

export default function Onboarding() {
  const navigate = useNavigate();
  const { checkAuth } = useAuth();
  const fileInputRef = useRef(null);
  const [username, setUsername] = useState('');
  const [selectedAvatar, setSelectedAvatar] = useState(0);
  const [customAvatarFile, setCustomAvatarFile] = useState(null);
  const [customAvatarPreview, setCustomAvatarPreview] = useState(null);
  const [favoriteClub, setFavoriteClub] = useState('');
  const [country, setCountry] = useState('');
  const [age, setAge] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [marketingConsent, setMarketingConsent] = useState(false);
  const [clubsByLeague, setClubsByLeague] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadClubs();
  }, []);

  const loadClubs = async () => {
    try {
      const response = await clubs.getAll();
      setClubsByLeague(response.data);
    } catch (err) {
      console.error('Failed to load clubs:', err);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setError('Image must be under 5MB');
        return;
      }
      setCustomAvatarFile(file);
      setCustomAvatarPreview(URL.createObjectURL(file));
      setSelectedAvatar(-1);
    }
  };

  const getAvatarUrl = (seed) => `https://api.dicebear.com/7.x/avataaars/svg?seed=${seed}`;

  const isFormValid = username && username.length >= 3 && favoriteClub && country && age && phoneNumber;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isFormValid) return;
    setError('');
    setLoading(true);

    try {
      let avatarUrl;
      if (customAvatarFile) {
        const uploadRes = await users.uploadAvatar(customAvatarFile);
        avatarUrl = uploadRes.data.avatar;
      } else {
        avatarUrl = getAvatarUrl(FOOTBALL_AVATARS[selectedAvatar].seed);
      }

      await users.updateProfile({
        username,
        avatar: avatarUrl,
        favorite_club: favoriteClub,
        country,
        age: parseInt(age),
        phone_number: phoneNumber,
        marketing_consent: marketingConsent,
      });
      await checkAuth();
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const triggerClass = "w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white px-4 outline-none transition-all data-[placeholder]:text-white/30";
  const contentClass = "bg-[#1a1a2e] border-2 border-neon-blue/30 text-white max-h-[300px]";
  const itemClass = "text-white focus:bg-neon-blue/20 focus:text-neon-blue cursor-pointer";

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-[#1a1a2e] to-background flex items-center justify-center p-5">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <h1 className="text-5xl font-extrabold tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow mb-3">
            QuizBall
          </h1>
          <PoweredByScore90 size="md" className="justify-center mb-3" />
          <p className="text-base text-gray-300">
            Prove your <span className="text-neon-yellow font-bold">Ball Knowledge</span>
          </p>
        </div>

        <div className="bg-card border-2 border-neon-blue/30 rounded-lg p-6 shadow-2xl shadow-neon-blue/20 backdrop-blur-sm">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Avatar Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-3 uppercase tracking-wide">
                Choose Your Player
              </label>
              <div className="grid grid-cols-5 gap-2">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  data-testid="avatar-upload-btn"
                  className={`aspect-square rounded-lg border-2 border-dashed transition-all flex flex-col items-center justify-center gap-0.5 ${
                    customAvatarPreview ? 'border-neon-pink shadow-neon-pink' : 'border-white/30 hover:border-neon-blue/60'
                  }`}
                >
                  {customAvatarPreview ? (
                    <img src={customAvatarPreview} alt="Custom" className="w-full h-full rounded-lg object-cover" />
                  ) : (
                    <>
                      <Camera size={14} className="text-gray-400" />
                      <span className="text-[9px] text-gray-500">Upload</span>
                    </>
                  )}
                </button>
                <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileSelect} className="hidden" data-testid="avatar-file-input" />

                {FOOTBALL_AVATARS.slice(0, 4).map((avatar, index) => (
                  <button
                    key={avatar.seed}
                    type="button"
                    onClick={() => { setSelectedAvatar(index); setCustomAvatarFile(null); setCustomAvatarPreview(null); }}
                    data-testid={`avatar-${index}`}
                    className={`aspect-square rounded-lg border-2 transition-all relative overflow-hidden ${
                      selectedAvatar === index && !customAvatarPreview ? 'border-neon-pink shadow-neon-pink' : 'border-white/20 hover:border-neon-blue/40'
                    }`}
                  >
                    <img src={getAvatarUrl(avatar.seed)} alt={avatar.label} className="w-full h-full rounded-lg" />
                    <span className="absolute bottom-0 inset-x-0 bg-black/70 text-[8px] text-center text-gray-300 py-0.5 font-bold uppercase">{avatar.label}</span>
                  </button>
                ))}
              </div>
              <div className="grid grid-cols-5 gap-2 mt-2">
                <div />
                {FOOTBALL_AVATARS.slice(4).map((avatar, index) => (
                  <button
                    key={avatar.seed}
                    type="button"
                    onClick={() => { setSelectedAvatar(index + 4); setCustomAvatarFile(null); setCustomAvatarPreview(null); }}
                    data-testid={`avatar-${index + 4}`}
                    className={`aspect-square rounded-lg border-2 transition-all relative overflow-hidden ${
                      selectedAvatar === index + 4 && !customAvatarPreview ? 'border-neon-pink shadow-neon-pink' : 'border-white/20 hover:border-neon-blue/40'
                    }`}
                  >
                    <img src={getAvatarUrl(avatar.seed)} alt={avatar.label} className="w-full h-full rounded-lg" />
                    <span className="absolute bottom-0 inset-x-0 bg-black/70 text-[8px] text-center text-gray-300 py-0.5 font-bold uppercase">{avatar.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">Username</label>
              <input
                type="text"
                data-testid="username-input"
                value={username}
                onChange={(e) => setUsername(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                className="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white placeholder:text-white/30 px-4 outline-none transition-all"
                placeholder="footballmaster"
                required
                minLength={3}
                maxLength={20}
              />
              <p className="text-xs text-gray-500 mt-1">3-20 characters, lowercase letters, numbers, underscores</p>
            </div>

            {/* Favourite Club */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                Select Your Favourite Club
              </label>
              <Select value={favoriteClub} onValueChange={setFavoriteClub} data-testid="club-select-wrapper">
                <SelectTrigger className={triggerClass} data-testid="club-select">
                  <SelectValue placeholder="Select a club..." />
                </SelectTrigger>
                <SelectContent className={contentClass}>
                  {Object.entries(clubsByLeague).map(([league, clubList]) => (
                    <SelectGroup key={league}>
                      <SelectLabel className="text-neon-pink font-bold uppercase text-xs tracking-wider px-2 py-2">{league}</SelectLabel>
                      {clubList.map((club) => (
                        <SelectItem key={club} value={club} className={itemClass}>{club}</SelectItem>
                      ))}
                    </SelectGroup>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Country */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                Country of Residence
              </label>
              <Select value={country} onValueChange={setCountry}>
                <SelectTrigger className={triggerClass} data-testid="country-select">
                  <SelectValue placeholder="Select your country..." />
                </SelectTrigger>
                <SelectContent className={contentClass}>
                  {COUNTRIES.map((c) => (
                    <SelectItem key={c} value={c} className={itemClass}>{c}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Age & Phone */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">Age</label>
                <Select value={age} onValueChange={setAge}>
                  <SelectTrigger className={triggerClass} data-testid="age-select">
                    <SelectValue placeholder="Age" />
                  </SelectTrigger>
                  <SelectContent className={contentClass}>
                    {AGES.map((a) => (
                      <SelectItem key={a} value={a} className={itemClass}>{a}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">Mobile Phone</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-3.5 text-gray-500 z-10" size={18} />
                  <input
                    type="tel"
                    data-testid="phone-input"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white placeholder:text-white/30 pl-10 pr-4 outline-none transition-all"
                    placeholder="+44..."
                    required
                  />
                </div>
              </div>
            </div>

            {/* Marketing Consent */}
            <label className="flex items-start gap-3 cursor-pointer group" data-testid="marketing-consent-label">
              <div className="relative flex-shrink-0 mt-0.5">
                <input
                  type="checkbox"
                  checked={marketingConsent}
                  onChange={(e) => setMarketingConsent(e.target.checked)}
                  className="sr-only peer"
                  data-testid="marketing-consent-checkbox"
                />
                <div className="w-5 h-5 rounded border-2 border-neon-blue/40 bg-black/50 peer-checked:bg-neon-blue peer-checked:border-neon-blue transition-all flex items-center justify-center group-hover:border-neon-blue/70">
                  {marketingConsent && (
                    <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="none">
                      <path d="M2 6l3 3 5-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </div>
              </div>
              <span className="text-xs text-gray-400 leading-relaxed">
                I'd like to receive news, updates, and promotional offers from QuizBall and Score90 via email and push notifications. You can unsubscribe at any time. See our <a href="#" className="text-neon-blue hover:text-neon-pink underline">Privacy Policy</a>.
              </span>
            </label>

            {error && (
              <div className="bg-destructive/10 border-2 border-destructive rounded-sm p-3 text-sm text-destructive" data-testid="onboarding-error">
                {error}
              </div>
            )}

            <button
              type="submit"
              data-testid="continue-btn"
              disabled={loading || !isFormValid}
              className={`w-full h-12 px-6 rounded-sm font-bold uppercase tracking-wider transition-all active:scale-95 text-white ${
                isFormValid && !loading
                  ? 'bg-gradient-to-r from-neon-blue via-neon-pink to-neon-yellow hover:from-neon-yellow hover:via-neon-pink hover:to-neon-blue shadow-neon-blue hover:shadow-neon-pink cursor-pointer'
                  : 'bg-gray-700 cursor-not-allowed opacity-50'
              }`}
            >
              {loading ? 'Saving...' : 'Continue to QuizBall'}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
