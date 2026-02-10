import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Phone, Camera } from 'lucide-react';
import { users, clubs } from '../lib/api';
import { PoweredByScore90 } from '../components/Score90Logo';
import { useAuth } from '../context/AuthContext';

const FOOTBALL_AVATARS = [
  { seed: 'Goalkeeper', label: 'Keeper' },
  { seed: 'Striker', label: 'Striker' },
  { seed: 'Midfielder', label: 'Mid' },
  { seed: 'Defender', label: 'Defender' },
  { seed: 'Captain', label: 'Captain' },
  { seed: 'Winger', label: 'Winger' },
  { seed: 'Playmaker', label: 'Maker' },
  { seed: 'FreeKick', label: 'FK' },
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

const AGES = Array.from({ length: 88 }, (_, i) => i + 12);

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
    } catch (error) {
      console.error('Failed to load clubs:', error);
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

  const getAvatarUrl = (seed) => `https://api.dicebear.com/7.x/bottts-neutral/svg?seed=${seed}&backgroundColor=1a1a2e`;

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
      });
      await checkAuth();
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const selectClass = "w-full bg-black/50 border-2 border-neon-blue/30 focus:border-neon-pink focus:ring-2 focus:ring-neon-pink/50 h-12 rounded-sm text-white px-4 outline-none transition-all appearance-none";

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
                {/* Upload button */}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  data-testid="avatar-upload-btn"
                  className={`aspect-square rounded-lg border-2 border-dashed transition-all flex flex-col items-center justify-center gap-0.5 ${
                    customAvatarPreview
                      ? 'border-neon-pink shadow-neon-pink'
                      : 'border-white/30 hover:border-neon-blue/60'
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
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                  data-testid="avatar-file-input"
                />

                {/* Football avatars row 1 */}
                {FOOTBALL_AVATARS.slice(0, 4).map((avatar, index) => (
                  <button
                    key={avatar.seed}
                    type="button"
                    onClick={() => { setSelectedAvatar(index); setCustomAvatarFile(null); setCustomAvatarPreview(null); }}
                    data-testid={`avatar-${index}`}
                    className={`aspect-square rounded-lg border-2 transition-all relative overflow-hidden ${
                      selectedAvatar === index && !customAvatarPreview
                        ? 'border-neon-pink shadow-neon-pink'
                        : 'border-white/20 hover:border-neon-blue/40'
                    }`}
                  >
                    <img
                      src={getAvatarUrl(avatar.seed)}
                      alt={avatar.label}
                      className="w-full h-full rounded-lg"
                    />
                    <span className="absolute bottom-0 inset-x-0 bg-black/70 text-[8px] text-center text-gray-300 py-0.5 font-bold uppercase">{avatar.label}</span>
                  </button>
                ))}
              </div>
              {/* Row 2 */}
              <div className="grid grid-cols-5 gap-2 mt-2">
                <div></div>
                {FOOTBALL_AVATARS.slice(4).map((avatar, index) => (
                  <button
                    key={avatar.seed}
                    type="button"
                    onClick={() => { setSelectedAvatar(index + 4); setCustomAvatarFile(null); setCustomAvatarPreview(null); }}
                    data-testid={`avatar-${index + 4}`}
                    className={`aspect-square rounded-lg border-2 transition-all relative overflow-hidden ${
                      selectedAvatar === index + 4 && !customAvatarPreview
                        ? 'border-neon-pink shadow-neon-pink'
                        : 'border-white/20 hover:border-neon-blue/40'
                    }`}
                  >
                    <img
                      src={getAvatarUrl(avatar.seed)}
                      alt={avatar.label}
                      className="w-full h-full rounded-lg"
                    />
                    <span className="absolute bottom-0 inset-x-0 bg-black/70 text-[8px] text-center text-gray-300 py-0.5 font-bold uppercase">{avatar.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                Username
              </label>
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

            {/* Favorite Club */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                Select Your Favourite Club
              </label>
              <select
                data-testid="club-select"
                value={favoriteClub}
                onChange={(e) => setFavoriteClub(e.target.value)}
                className={selectClass}
                required
              >
                <option value="" className="bg-card">Select a club...</option>
                {Object.entries(clubsByLeague).map(([league, clubList]) => (
                  <optgroup key={league} label={league} className="bg-card">
                    {clubList.map((club) => (
                      <option key={club} value={club} className="bg-card">{club}</option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>

            {/* Country */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                Country of Residence
              </label>
              <select
                data-testid="country-select"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className={selectClass}
                required
              >
                <option value="" className="bg-card">Select your country...</option>
                {COUNTRIES.map((c) => (
                  <option key={c} value={c} className="bg-card">{c}</option>
                ))}
              </select>
            </div>

            {/* Age & Phone */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                  Age
                </label>
                <select
                  data-testid="age-select"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  className={selectClass}
                  required
                >
                  <option value="" className="bg-card">Age</option>
                  {AGES.map((a) => (
                    <option key={a} value={a} className="bg-card">{a}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2 uppercase tracking-wide">
                  Mobile Phone
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-3.5 text-gray-500" size={18} />
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
