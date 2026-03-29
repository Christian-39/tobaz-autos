import { useState } from 'react'
import { Camera, Save } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useAuth } from '@/contexts/AuthContext'
import { authApi } from '@/lib/api'
import { getInitials } from '@/lib/utils'

export default function Profile() {
  const { user, updateUser } = useAuth()
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    address: user?.address || '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      setSaving(true)
      const updated = await authApi.updateProfile(formData)
      updateUser(updated as any)
      toast.success('Profile updated')
    } catch (error) {
      toast.error('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    try {
      const response = await authApi.uploadProfileImage(file)
      updateUser({ ...user!, profile_image: (response as any).profile_image })
      toast.success('Profile image updated')
    } catch (error) {
      toast.error('Failed to upload image')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Profile</h1>
        <p className="text-muted-foreground mt-1">Manage your profile information</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Profile Image */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col items-center">
              <div className="relative">
                <Avatar className="h-32 w-32">
                  <AvatarImage src={user?.profile_image} />
                  <AvatarFallback className="text-4xl">
                    {getInitials(user?.full_name || 'U')}
                  </AvatarFallback>
                </Avatar>
                <label className="absolute bottom-0 right-0 p-2 bg-primary rounded-full cursor-pointer hover:bg-primary/90">
                  <Camera className="h-4 w-4 text-primary-foreground" />
                  <input
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleImageUpload}
                  />
                </label>
              </div>
              <h3 className="mt-4 text-xl font-semibold">{user?.full_name}</h3>
              <p className="text-muted-foreground capitalize">{user?.role}</p>
            </div>
          </CardContent>
        </Card>

        {/* Profile Form */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>First Name</Label>
                  <Input
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Last Name</Label>
                  <Input
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Phone</Label>
                <Input
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Address</Label>
                <Input
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                />
              </div>
              <div className="flex justify-end">
                <Button type="submit" disabled={saving}>
                  {saving ? (
                    'Saving...'
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save Changes
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
